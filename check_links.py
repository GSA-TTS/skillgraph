#!/usr/bin/env python3
"""
check_links.py — Validates URLs found in a markdown file and reports issues.

Usage:
    python check_links.py [-h] [-toplv TLD] [-env {within,external}]
                          [-i INPUT] [-o OUTPUT] [-t TIMEOUT] [-d DELAY]
                          [-r PREV_CSV] [--no-ssl-verify]

Each URL is checked three ways:
  1. Structural validation (format, doubled URLs, bad hostnames)
  2. DNS resolution
  3. HTTP HEAD request (with GET fallback)

Pass -r / --recheck with a previous output CSV to re-check only the
URLs that had errors, while preserving OK rows from the original run.
"""

# ── stdlib ────────────────────────────────────────────────────────────────────
import argparse
import concurrent.futures
import csv
import ipaddress
import re
import socket
import sys
import time
import random
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple
from urllib.parse import urlparse

# ── third-party (checked lazily so we can print remedial guidance) ────────────
_MISSING_REQUIRED: List[str] = []
_MISSING_OPTIONAL: List[str] = []

try:
    import requests  # type: ignore[import-untyped]
    from requests.adapters import HTTPAdapter, Retry  # type: ignore[import-untyped]
    from requests.exceptions import (  # type: ignore[import-untyped]
        ConnectionError as ReqConnError,
        RequestException as ReqError,
        SSLError as ReqSSLError,
        Timeout as ReqTimeout,
        TooManyRedirects as ReqTooManyRedirects,
    )
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False
    _MISSING_REQUIRED.append(
        "  requests   →  pip install requests"
    )
    # Provide stubs so the module parses cleanly before check_deps() exits.
    requests = None  # type: ignore[assignment]
    HTTPAdapter = None  # type: ignore[assignment,misc]
    Retry = None  # type: ignore[assignment,misc]
    ReqConnError = Exception  # type: ignore[assignment,misc]
    ReqError = Exception  # type: ignore[assignment,misc]
    ReqSSLError = Exception  # type: ignore[assignment,misc]
    ReqTimeout = Exception  # type: ignore[assignment,misc]
    ReqTooManyRedirects = Exception  # type: ignore[assignment,misc]


# ── Constants ─────────────────────────────────────────────────────────────────

_USER_AGENTS: List[str] = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
        "Gecko/20100101 Firefox/121.0"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.2 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
]

_BASE_HEADERS: Dict[str, str] = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "DNT": "1",
    "Cache-Control": "max-age=0",
}

# Domains that typically require VPN / internal network access.
_RESTRICTED_DOMAINS: Set[str] = {
    "insite.gsa.gov",
    "community.max.gov",
}

# Markdown link:  [Name](URL)
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")

# Raw URL not preceded by '(' (i.e. not the URL part of a markdown link).
_RAW_URL_RE = re.compile(
    r"(?<!\()https?://[^\s|\])\'\"><{}\[\]]+",
    re.IGNORECASE,
)

_URL_TRAILING_JUNK = frozenset(".,;:!?)'\"\\ ")

DEFAULT_TIMEOUT: float = 15.0
DEFAULT_DELAY: float = 1.5
DEFAULT_OUTPUT = "link_check_results.csv"
DEFAULT_INPUT = "trainings.md"


# ── Data structures ───────────────────────────────────────────────────────────


class LinkEntry(NamedTuple):
    seq: int
    name: str
    url: str
    original_url: str
    line_num: int
    parse_notes: List[str]


# ── Dependency / startup checks ───────────────────────────────────────────────


def check_deps() -> None:
    """Print remedial guidance and exit if required packages are missing."""
    if _MISSING_REQUIRED:
        print(
            "FATAL — Required packages are missing. Install them and re-run:\n",
            file=sys.stderr,
        )
        for pkg in _MISSING_REQUIRED:
            print(pkg, file=sys.stderr)
        sys.exit(1)

    if _MISSING_OPTIONAL:
        print("INFO — Optional packages not installed (non-critical):")
        for pkg in _MISSING_OPTIONAL:
            print(pkg)
        print()


# ── URL helpers ───────────────────────────────────────────────────────────────


def _clean_url(raw: str) -> Tuple[str, List[str]]:
    """Strip trailing punctuation/quotes from a URL; return (url, warnings)."""
    notes: List[str] = []
    url = raw
    while url and url[-1] in _URL_TRAILING_JUNK:
        url = url[:-1]
    if url != raw:
        notes.append(f"Stripped trailing chars from URL (was {raw!r})")
    return url, notes


def _tld_of(url: str) -> str:
    """Return the top-level domain of a URL, e.g. 'gov' or 'com'."""
    try:
        host = urlparse(url).hostname or ""
        return host.rsplit(".", 1)[-1].lower() if "." in host else host.lower()
    except Exception:
        return ""


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _validate_structure(url: str) -> Tuple[bool, str]:
    """
    Return (is_ok, reason) for basic structural checks.

    Detects: bad scheme, no hostname, single-label hostnames (e.g. 'V'),
    and doubled / concatenated URLs.
    """
    try:
        parsed = urlparse(url)
    except Exception as exc:
        return False, f"URL parse error: {exc}"

    if parsed.scheme not in ("http", "https"):
        return False, f"Unsupported scheme: {parsed.scheme!r}"

    host = parsed.hostname or ""
    if not host:
        return False, "No hostname in URL"

    # Reject single-label hostnames that are not IP addresses (e.g. 'V').
    if "." not in host and not _is_ip(host):
        return False, (
            f"Invalid hostname — no dots and not an IP address: {host!r}"
        )

    # Detect concatenated URLs (e.g. ...646ahttps://...).
    after_scheme = url[url.index("://") + 3:]
    for marker in ("https://", "http://"):
        pos = after_scheme.find(marker)
        if pos > 0:
            return False, (
                f"Appears to be two concatenated URLs. "
                f"Second URL starts at position {pos + len(url) - len(after_scheme)}"
            )

    return True, ""


# ── Link extraction ───────────────────────────────────────────────────────────


def extract_links(file_path: Path) -> List[LinkEntry]:
    """
    Parse a markdown file and return one LinkEntry per unique URL.

    Captures both [Name](URL) markdown links and bare https?:// URLs.
    Deduplicates by cleaned URL.
    """
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    seen: Set[str] = set()
    entries: List[LinkEntry] = []
    seq = 0

    for line_num, line in enumerate(lines, 1):
        # ── Markdown links ────────────────────────────────────────────────
        for m in _MD_LINK_RE.finditer(line):
            name = m.group(1).strip() or "(no title)"
            raw = m.group(2).strip()
            url, pnotes = _clean_url(raw)
            if url and url not in seen:
                seen.add(url)
                seq += 1
                entries.append(
                    LinkEntry(
                        seq=seq,
                        name=name,
                        url=url,
                        original_url=raw,
                        line_num=line_num,
                        parse_notes=pnotes,
                    )
                )

        # ── Raw URLs (after removing markdown link syntax) ────────────────
        stripped = _MD_LINK_RE.sub("", line)
        for m in _RAW_URL_RE.finditer(stripped):
            raw = m.group(0)
            url, pnotes = _clean_url(raw)
            if url and url not in seen:
                seen.add(url)
                seq += 1
                entries.append(
                    LinkEntry(
                        seq=seq,
                        name=url,
                        url=url,
                        original_url=raw,
                        line_num=line_num,
                        parse_notes=pnotes,
                    )
                )

    return entries


# ── Recheck helpers ──────────────────────────────────────────────────────────


def load_recheck_csv(
    csv_path: Path,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Read a previous results CSV and split rows into ok / bad.

    ok_rows  — result starts with 'OK'; passed through unchanged.
    bad_rows — everything else; will be re-checked.
    """
    expected = {"number", "name", "url", "result", "notes"}
    ok_rows: List[Dict[str, Any]] = []
    bad_rows: List[Dict[str, Any]] = []

    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames and not expected.issubset(set(reader.fieldnames)):
            missing = expected - set(reader.fieldnames)
            print(
                f"WARNING: Recheck CSV is missing columns: {missing}. "
                "Proceeding anyway.",
                file=sys.stderr,
            )
        for row in reader:
            bucket = (
                ok_rows
                if row.get("result", "").startswith("OK")
                else bad_rows
            )
            bucket.append(dict(row))

    return ok_rows, bad_rows


def _csv_rows_to_entries(rows: List[Dict[str, Any]]) -> List[LinkEntry]:
    """Convert raw CSV row dicts to LinkEntry objects for re-checking."""
    entries: List[LinkEntry] = []
    for row in rows:
        url = row.get("url", "").strip()
        if not url:
            continue
        try:
            seq = int(row.get("number", 0))
        except (ValueError, TypeError):
            seq = 0
        name = row.get("name", url).strip() or url
        entries.append(
            LinkEntry(
                seq=seq,
                name=name,
                url=url,
                original_url=url,
                line_num=0,
                parse_notes=[],
            )
        )
    return entries


# ── Network checks ────────────────────────────────────────────────────────────


def _dns_check(hostname: str, timeout: float) -> Tuple[bool, str]:
    """
    Resolve hostname in a thread so we can enforce a timeout cleanly.

    Returns (resolved_ok, message).
    """

    def _resolve() -> None:
        # Set timeout inside the thread to avoid mutating global state
        # from the main thread.
        socket.setdefaulttimeout(timeout)
        try:
            socket.getaddrinfo(hostname, None)
        finally:
            socket.setdefaulttimeout(None)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(_resolve)
        try:
            fut.result(timeout=timeout + 1)
            return True, "DNS OK"
        except concurrent.futures.TimeoutError:
            return False, "DNS lookup timed out"
        except socket.gaierror as exc:
            return False, f"DNS error — {exc}"
        except OSError as exc:
            return False, f"DNS OS error — {exc}"
        except Exception as exc:  # noqa: BLE001
            return False, f"DNS check failed — {exc}"


def _browser_headers() -> Dict[str, str]:
    """Return headers that mimic a legitimate browser (rotated User-Agent)."""
    headers = dict(_BASE_HEADERS)
    headers["User-Agent"] = random.choice(_USER_AGENTS)  # nosec B311
    return headers


def _http_status_label(code: int) -> str:
    if 200 <= code < 300:
        return f"OK ({code})"
    if 300 <= code < 400:
        return f"REDIRECT ({code})"
    labels = {
        401: "UNAUTHORIZED (401)",
        403: "FORBIDDEN (403)",
        404: "NOT FOUND (404)",
        410: "GONE (410)",
        429: "RATE LIMITED (429)",
    }
    if code in labels:
        return labels[code]
    if 400 <= code < 500:
        return f"CLIENT ERROR ({code})"
    if 500 <= code < 600:
        return f"SERVER ERROR ({code})"
    return f"HTTP {code}"


def _http_check(
    url: str,
    session: Any,
    timeout: float,
    verify_ssl: bool,
) -> Tuple[str, Optional[int], Optional[str], List[str]]:
    """
    Try HEAD then GET; return (status_label, http_code, final_url, notes).

    Some servers refuse HEAD or return misleading codes for it, so GET is
    used as a second verification method when HEAD produces 4xx or fails.
    """
    notes: List[str] = []
    head_code: Optional[int] = None
    head_final: Optional[str] = None

    # (connect_timeout, read_timeout) — split so a server that accepts the
    # TCP handshake but never sends HTTP data still trips the read timeout.
    req_timeout = (5.0, timeout)

    # ── Check 1: HEAD ─────────────────────────────────────────────────────
    try:
        resp = session.head(
            url,
            headers=_browser_headers(),
            timeout=req_timeout,
            allow_redirects=True,
            verify=verify_ssl,
        )
        head_code = resp.status_code
        head_final = resp.url

        if head_final and head_final != url:
            notes.append(f"Redirected (HEAD) → {head_final}")

        # HEAD success — skip GET unless the result is suspicious.
        if head_code < 400 or head_code in (200, 206):
            return _http_status_label(head_code), head_code, head_final, notes

        # 405 = Method Not Allowed; 403/501 can also be HEAD-hostile.
        if head_code in (403, 405, 501):
            notes.append(
                f"HEAD returned {head_code} (server may not support HEAD)"
            )
        else:
            notes.append(f"HEAD returned {head_code}; confirming with GET")

    except ReqTimeout:
        notes.append("HEAD request timed out")
    except ReqSSLError as exc:
        return "SSL ERROR", None, None, [f"SSL/TLS error — {exc}"]
    except ReqTooManyRedirects:
        return "TOO MANY REDIRECTS", None, None, ["Redirect loop or chain > 30"]
    except ReqConnError as exc:
        notes.append(f"HEAD connection error — {exc}")
    except ReqError as exc:
        notes.append(f"HEAD request error — {exc}")

    # Small jitter before second request to simulate human pacing.
    time.sleep(random.uniform(0.3, 0.9))  # nosec B311

    # ── Check 2: GET ──────────────────────────────────────────────────────
    try:
        resp = session.get(
            url,
            headers=_browser_headers(),
            timeout=req_timeout,
            allow_redirects=True,
            verify=verify_ssl,
            stream=True,  # Avoid downloading the full body.
        )
        resp.close()
        code = resp.status_code
        final = resp.url

        if final and final != url and final != head_final:
            notes.append(f"Redirected (GET) → {final}")
        if head_code is not None and head_code != code:
            notes.append(f"HEAD={head_code} vs GET={code}")

        return _http_status_label(code), code, final, notes

    except ReqTimeout:
        if head_code is not None:
            notes.append("GET timed out (using HEAD result)")
            return _http_status_label(head_code), head_code, head_final, notes
        return "TIMEOUT", None, None, notes + ["Both HEAD and GET timed out"]
    except ReqSSLError as exc:
        return "SSL ERROR", None, None, notes + [f"SSL/TLS error (GET) — {exc}"]
    except ReqTooManyRedirects:
        return (
            "TOO MANY REDIRECTS",
            None,
            None,
            notes + ["Redirect loop (GET)"],
        )
    except ReqConnError as exc:
        return (
            "CONNECTION ERROR",
            None,
            None,
            notes + [f"Connection error (GET) — {exc}"],
        )
    except ReqError as exc:
        return "REQUEST ERROR", None, None, notes + [f"GET error — {exc}"]


def check_url(
    url: str,
    session: Any,
    timeout: float,
    verify_ssl: bool,
) -> Tuple[str, Optional[int], Optional[str], List[str]]:
    """
    Full three-method check: structure → DNS → HTTP (HEAD + GET).

    Returns (status_label, http_code, final_url, detail_notes).
    """
    ok, reason = _validate_structure(url)
    if not ok:
        return "INVALID URL", None, None, [reason]

    host = urlparse(url).hostname or ""
    dns_ok, dns_msg = _dns_check(host, min(timeout, 5.0))
    if not dns_ok:
        return "DNS ERROR", None, None, [dns_msg]

    # Run HTTP check in a thread with a hard wall-clock deadline.
    # This catches TLS handshake hangs that socket-level timeouts miss on
    # macOS/some networks (server accepts TCP but stalls on TLS negotiation).
    # IMPORTANT: do NOT use `with ThreadPoolExecutor` here — its __exit__
    # calls shutdown(wait=True) which blocks until the stuck thread finishes,
    # defeating the purpose entirely.
    wall_limit = timeout + 3  # hard cap: if HEAD already used full timeout, skip GET
    _ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    _fut = _ex.submit(_http_check, url, session, timeout, verify_ssl)
    try:
        result = _fut.result(timeout=wall_limit)
        _ex.shutdown(wait=False)
        return result
    except concurrent.futures.TimeoutError:
        _ex.shutdown(wait=False)  # Let stuck thread die on its own.
        return (
            "TIMEOUT",
            None,
            None,
            [
                f"Wall-clock timeout after {wall_limit:.0f}s — "
                "server accepted TCP but stalled (likely TLS handshake hang)"
            ],
        )
    except Exception as exc:  # noqa: BLE001
        _ex.shutdown(wait=False)
        return "REQUEST ERROR", None, None, [f"Unexpected: {exc}"]


# ── Session builder ───────────────────────────────────────────────────────────


def _make_session() -> Any:
    """Build a requests Session with retry logic for transient server errors."""
    session = requests.Session()
    try:
        retry = Retry(
            total=2,
            read=False,     # Never retry on read timeouts — they mask hangs.
            connect=1,      # One retry on connect errors only.
            backoff_factor=0.6,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
            raise_on_status=False,
        )
    except TypeError:
        # Older urllib3 uses method_whitelist instead of allowed_methods.
        retry = Retry(
            total=2,
            read=False,
            backoff_factor=0.6,
            status_forcelist=[500, 502, 503, 504],
        )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


# ── CLI ───────────────────────────────────────────────────────────────────────


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Check URLs in a markdown file for reachability issues. "
            "Results are written to a CSV file."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "-toplv",
        dest="tld",
        default=None,
        metavar="TLD",
        help=(
            "Only scan URLs whose top-level domain matches "
            "(e.g., gov  com  edu). Default: scan all TLDs."
        ),
    )
    p.add_argument(
        "-env",
        dest="env",
        choices=["within", "external"],
        default="external",
        help=(
            "Scanning environment: 'external' (outside agency network) "
            "or 'within' (inside VPN/intranet). "
            "Affects Notes — does not change which URLs are requested."
        ),
    )
    p.add_argument(
        "-i",
        "--input",
        dest="input_file",
        default=DEFAULT_INPUT,
        help="Markdown file to parse for URLs.",
    )
    p.add_argument(
        "-o",
        "--output",
        dest="output_file",
        default=DEFAULT_OUTPUT,
        help="Output CSV file path.",
    )
    p.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Per-request timeout in seconds.",
    )
    p.add_argument(
        "-d",
        "--delay",
        dest="delay",
        type=float,
        default=DEFAULT_DELAY,
        help=(
            "Base delay between requests in seconds "
            "(±0.5 s random jitter is added automatically)."
        ),
    )
    p.add_argument(
        "-r",
        "--recheck",
        dest="recheck_file",
        default=None,
        metavar="CSV_FILE",
        help=(
            "Re-check only the failed/errored URLs from a previous run's "
            "output CSV. OK rows from that run are preserved unchanged in "
            "the new output. Replaces -i when provided."
        ),
    )
    p.add_argument(
        "--no-ssl-verify",
        dest="no_ssl_verify",
        action="store_true",
        default=False,
        help=(
            "Disable SSL certificate verification. "
            "Use only when scanning internal sites with self-signed certs."
        ),
    )
    return p.parse_args()


def main() -> None:
    check_deps()
    args = _parse_args()

    verify_ssl: bool = not args.no_ssl_verify
    tld_filter: Optional[str] = (
        args.tld.lower().lstrip(".") if args.tld else None
    )

    # Global socket backstop — catches SSL handshake hangs that per-request
    # timeouts miss (e.g. servers that accept TCP but stall on TLS).
    socket.setdefaulttimeout(args.timeout + 3)

    # Notes prefix — encodes every active switch, prepended to every row.
    switch_notes = f"env={args.env}. tld={tld_filter or 'all'}"
    if args.no_ssl_verify:
        switch_notes += ". ssl-verify=disabled"

    # Rows carried over from a previous run unchanged (recheck mode only).
    passthrough_rows: List[Dict[str, Any]] = []
    # Previous result strings keyed by URL (for "Previously: X" notes).
    prev_results: Dict[str, str] = {}

    # ── Source: recheck CSV or fresh markdown scan ────────────────────────
    if args.recheck_file:
        recheck_path = Path(args.recheck_file)
        if not recheck_path.exists():
            print(
                f"ERROR: Recheck file not found: {recheck_path}",
                file=sys.stderr,
            )
            sys.exit(1)

        switch_notes += f". recheck={recheck_path.name}"
        print(f"Loading previous results from {recheck_path} …")
        ok_rows, bad_rows = load_recheck_csv(recheck_path)
        print(
            f"  {len(ok_rows)} OK rows (pass-through), "
            f"{len(bad_rows)} rows to re-check."
        )

        all_bad = _csv_rows_to_entries(bad_rows)
        bad_by_url = {row["url"]: row for row in bad_rows}
        prev_results = {row["url"]: row.get("result", "") for row in bad_rows}

        if tld_filter:
            links = [e for e in all_bad if _tld_of(e.url) == tld_filter]
            # Bad URLs outside the TLD filter pass through unchanged too.
            skipped_urls = {e.url for e in all_bad if _tld_of(e.url) != tld_filter}
            passthrough_rows = ok_rows + [
                bad_by_url[u] for u in skipped_urls if u in bad_by_url
            ]
            print(
                f"  Filtered to {len(links)} bad URLs with TLD=.{tld_filter}."
            )
        else:
            links = all_bad
            passthrough_rows = ok_rows

    else:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(
                f"ERROR: Input file not found: {input_path}",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"Parsing {input_path} …")
        all_links = extract_links(input_path)
        print(f"  Found {len(all_links)} unique URLs.")

        if tld_filter:
            links = [e for e in all_links if _tld_of(e.url) == tld_filter]
            print(f"  Filtered to {len(links)} URLs with TLD=.{tld_filter}.")
        else:
            links = all_links

    if not links:
        print("No URLs to check. Exiting.")
        sys.exit(0)

    # ── Check ─────────────────────────────────────────────────────────────
    session = _make_session()
    checked_rows: List[Dict[str, Any]] = []
    total = len(links)

    for i, entry in enumerate(links, 1):
        print(f"  [{i}/{total}] {entry.url[:72]}", flush=True)

        detail_notes: List[str] = list(entry.parse_notes)

        # In recheck mode, surface the previous result for comparison.
        if entry.url in prev_results and prev_results[entry.url]:
            detail_notes.append(
                f"Previously: {prev_results[entry.url]}"
            )

        # Warn about restricted / internal-only domains when outside network.
        host = urlparse(entry.url).hostname or ""
        if args.env == "external" and host in _RESTRICTED_DOMAINS:
            detail_notes.append(
                f"Domain '{host}' is internal/restricted — "
                "results may fail or require authentication from outside VPN"
            )

        status, _code, _final, check_notes = check_url(
            entry.url, session, args.timeout, verify_ssl
        )
        detail_notes.extend(check_notes)

        details_str = ". ".join(n for n in detail_notes if n)
        full_notes = (
            f"{switch_notes}. {details_str}" if details_str else switch_notes
        )

        checked_rows.append(
            {
                "number": entry.seq,
                "name": entry.name,
                "url": entry.url,
                "result": status,
                "notes": full_notes,
            }
        )

        # Rate-limit with random jitter to simulate natural browsing cadence.
        time.sleep(max(0.0, args.delay + random.uniform(-0.5, 0.5)))  # nosec B311

    # ── Merge and write CSV ───────────────────────────────────────────────
    # Combine pass-through rows with freshly checked rows, restore order.
    all_rows = passthrough_rows + checked_rows
    try:
        all_rows.sort(key=lambda r: int(r.get("number", 0)))
    except (ValueError, TypeError):
        pass  # Non-integer numbers: preserve append order.

    output_path = Path(args.output_file)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["number", "name", "url", "result", "notes"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(all_rows)

    # ── Summary ───────────────────────────────────────────────────────────
    ok_count = sum(1 for r in all_rows if r["result"].startswith("OK"))
    issue_count = len(all_rows) - ok_count
    rechecked = len(checked_rows)
    passthrough = len(passthrough_rows)

    print(f"\nResults written → {output_path}")
    if passthrough:
        pt_ok = sum(
            1 for r in passthrough_rows if r["result"].startswith("OK")
        )
        pt_skipped = passthrough - pt_ok
        print(
            f"  {passthrough} rows passed through from previous run "
            f"({pt_ok} OK + {pt_skipped} bad skipped by TLD filter)."
        )
    print(
        f"Summary: {ok_count} OK, {issue_count} with issues "
        f"(out of {len(all_rows)} total rows; {rechecked} checked this run)."
    )


if __name__ == "__main__":
    main()
