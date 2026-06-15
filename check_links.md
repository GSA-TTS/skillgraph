# check_links.py — URL Validator for trainings.md

Scans a markdown file for all URLs, checks each one for reachability issues,
and writes a CSV report. Supports targeted re-checking of previously failed
links without re-scanning URLs that already passed.

---

## Prerequisites

**Python 3.8+** is required.

### Required package

```
pip install requests
```

### Optional package (enables progress bar)

```
pip install tqdm
```

The script checks for missing packages at startup and prints exact install
commands before exiting, so you can run it once on a new machine and follow
the guidance.

---

## Quick Start

```bash
# Check all URLs in trainings.md (default)
python3 check_links.py

# Open the results
open link_check_results.csv      # macOS
start link_check_results.csv     # Windows
```

---

## All Options

| Switch | Short | Default | Description |
|---|---|---|---|
| `-toplv TLD` | | *(all)* | Only scan URLs whose top-level domain matches (e.g., `gov`, `com`, `edu`). Leading dot is optional: `gov` and `.gov` are equivalent. |
| `-env {within,external}` | | `external` | Scanning environment context. `external` = outside agency VPN/network; `within` = inside. Recorded in Notes on every row; also triggers warnings for known internal-only domains. |
| `-i FILE` | `--input` | `trainings.md` | Markdown file to parse for URLs. Ignored when `--recheck` is used. |
| `-o FILE` | `--output` | `link_check_results.csv` | Output CSV file path. |
| `-t SECONDS` | `--timeout` | `15.0` | Per-request timeout. Applies separately to DNS lookup, HEAD request, and GET request. |
| `-d SECONDS` | `--delay` | `1.5` | Base delay between requests (±0.5 s random jitter is added automatically to simulate natural browsing cadence). |
| `-r FILE` | `--recheck` | *(off)* | Path to a previous output CSV. Re-checks only the rows that were not `OK`; passes all `OK` rows through unchanged. See [Re-checking Failed Links](#re-checking-failed-links). |
| `--no-ssl-verify` | | `False` | Disable SSL certificate verification. Use only for internal sites with self-signed certs. |

---

## How URLs Are Checked

Each URL goes through three independent checks in sequence. A failure at
any step stops further checks for that URL.

### Step 1 — Structural Validation (no network)

Catches malformed URLs before any request is made:

- Missing or unsupported scheme (`ftp://`, bare paths)
- No hostname (`http://` with nothing after it)
- Single-label hostnames with no dots that are not IP addresses (e.g. `http://V`)
- Concatenated / doubled URLs (two `https://` tokens in one URL string)
- Trailing junk characters (`'`, `"`, `)`, `.`, etc.) stripped with a warning

### Step 2 — DNS Resolution

Resolves the hostname in a background thread with a hard timeout (the lesser
of the `-t` value or 6 seconds). Reports `DNS ERROR` if the host cannot be
resolved, which covers:

- Hostname does not exist (`NXDOMAIN`)
- DNS server unreachable or timed out
- Network not available

### Step 3 — HTTP Check (HEAD → GET)

**Check 3a — HEAD request** with full browser-simulated headers:

- Five real browser User-Agent strings, rotated randomly
- `Accept`, `Accept-Language`, `Accept-Encoding`, `Sec-Fetch-*`, `DNT`, `Cache-Control` headers
- Follows redirects; records the final destination URL
- If the server returns `200–299`: recorded as `OK`
- If the server returns `403`, `405`, or `501` (common HEAD-hostile responses): falls through to GET

**Check 3b — GET request** (fallback or confirmation):

- Used when HEAD returns a 4xx or fails entirely
- Uses `stream=True` to avoid downloading large bodies
- A second random User-Agent is selected
- Result compared with HEAD result; discrepancy noted in the Notes column

A 0.3–0.9 second random pause separates HEAD from GET within the same URL
to mimic realistic browsing gaps.

---

## Output CSV

The output file has five columns:

| Column | Description |
|---|---|
| `number` | Sequential row number (preserves original numbering in recheck mode) |
| `name` | Link text from the markdown file, or the URL itself for bare URLs |
| `url` | The cleaned URL that was checked |
| `result` | Short status label (see table below) |
| `notes` | Active switches + detailed diagnostic information, separated by `. ` |

### Result Values

| Result | Meaning |
|---|---|
| `OK (200)` | URL is reachable and returned HTTP 200 |
| `OK (206)` | Partial content (still reachable) |
| `REDIRECT (301)` / `REDIRECT (302)` | Permanent / temporary redirect (final URL noted in Notes) |
| `UNAUTHORIZED (401)` | Server requires authentication |
| `FORBIDDEN (403)` | Server refused access (may still be reachable with auth) |
| `NOT FOUND (404)` | Page does not exist |
| `GONE (410)` | Page permanently removed |
| `RATE LIMITED (429)` | Too many requests; try again later or increase `-d` |
| `CLIENT ERROR (4xx)` | Other 4xx error |
| `SERVER ERROR (5xx)` | Server-side error |
| `DNS ERROR` | Hostname could not be resolved |
| `TIMEOUT` | Both HEAD and GET timed out |
| `SSL ERROR` | TLS/certificate error |
| `TOO MANY REDIRECTS` | Redirect loop or chain longer than 30 hops |
| `CONNECTION ERROR` | TCP connection refused or reset |
| `REQUEST ERROR` | Other network-level error |
| `INVALID URL` | URL failed structural validation (never sent to network) |

### Notes Column Format

Every Notes cell begins with the active switch context, then appends details:

```
env=external. tld=gov. <detail 1>. <detail 2>
```

In recheck mode, the previous result is prepended to the details:

```
env=external. tld=all. recheck=link_check_results.csv. Previously: DNS ERROR. DNS OK. Redirected (GET) → https://…
```

---

## Re-checking Failed Links

Use `-r` / `--recheck` to load a previous output CSV and re-check only the
rows that were not `OK`:

```bash
# First full scan
python3 check_links.py -o run1.csv

# Re-check only the failures from run1.csv
python3 check_links.py -r run1.csv -o run2.csv
```

**What happens:**

1. `run1.csv` is loaded; rows are split into **OK** (pass-through) and **bad** (re-check).
2. Only the bad URLs are checked again.
3. The output `run2.csv` contains:
   - All OK rows from `run1.csv` — **unchanged**, original row numbers preserved.
   - Re-checked rows with **updated** result and notes; previous result is recorded in Notes as `Previously: …`.
4. Rows are sorted by original `number`.

**Combining with `-toplv`:**

```bash
# Re-check only failed .gov URLs
python3 check_links.py -r run1.csv -toplv gov -o run2_gov.csv
```

Bad URLs outside the `.gov` TLD are passed through unchanged alongside the
OK rows; only the `.gov` bad URLs are re-checked.

---

## Usage Examples

```bash
# Scan all URLs, default settings
python3 check_links.py

# Scan only .gov URLs from within the agency network
python3 check_links.py -toplv gov -env within

# Use a different input file and output path
python3 check_links.py -i my_links.md -o my_results.csv

# Longer timeout and slower pacing (good for flaky connections)
python3 check_links.py -t 30 -d 3.0

# Re-check failures from a previous run
python3 check_links.py -r link_check_results.csv

# Re-check .com failures only, skip SSL verification for internal proxy
python3 check_links.py -r link_check_results.csv -toplv com --no-ssl-verify

# Full help
python3 check_links.py --help
```

---

## Known Issues in trainings.md

The scanner automatically detects and flags these pre-existing problems:

| # | URL | Issue |
|---|---|---|
| 93 | `(ASSESSMENT) Oral Communication` entry | Two URLs concatenated into one (`…646ahttps://…646a`) |
| 174 | `Data Compliance Channel` entry | Trailing `'` in URL, stripped automatically |
| 189 | `(BOOK) Applied Economic Analysis…` | URL is `http://V` — invalid hostname |

---

## Notes on Specific Domain Types

### `gsa.csod.com` — GSA Learning Management System

These URLs require a GSA account to access. From outside the network they
typically return `200` (login redirect) or `403`. A `200` result does not
necessarily mean the content is viewable without authentication.

### `insite.gsa.gov` / `community.max.gov` — Internal domains

These are flagged automatically when `-env external` (the default). Run with
`-env within` from inside the agency VPN to get accurate results.

### `http://` URLs

Several links use plain HTTP instead of HTTPS. These will check successfully
if the server responds, but the script notes the scheme in the URL column.
Consider upgrading to HTTPS where possible.

### `share.percipio.com` / `gsa.percipio.com`

Percipio (Skillsoft) links require a GSA account. External scans will
typically see a `200` login-page redirect rather than the actual course.

---

## Troubleshooting

**`FATAL — Required packages are missing`**
Run `pip install requests` and retry.

**Every URL times out**
Your network may be blocking outbound HTTP. Try increasing the timeout
(`-t 30`) or testing from a different network. Check with
`curl -I https://www.gsa.gov` first.

**`SSL ERROR` on internal sites**
The site uses a self-signed or internal CA certificate. Run with
`--no-ssl-verify` when scanning from within the network.

**`RATE LIMITED (429)`**
The target server is throttling requests. Increase the delay (`-d 5`) and
re-run, or use `-r` to re-check only the rate-limited entries.

**`FORBIDDEN (403)` on known-good URLs**
Some servers block non-browser clients or HEAD requests even when the page
is publicly accessible. The script already falls back to GET; a `403` from
GET likely means the server actively blocks automated access. Manual
verification in a browser is the only reliable check.

**Large files take a long time**
trainings.md has ~269 unique URLs. At the default 1.5 s delay, a full scan
takes roughly 7–10 minutes. Use `-toplv gov` to scan a subset, or lower
`-d 0.5` if the network is stable and you are willing to risk rate limiting.
