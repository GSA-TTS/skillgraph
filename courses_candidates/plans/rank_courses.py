#!/usr/bin/env python3
"""Rank the 46 AI 101 course candidates.

Composite score (0-100):
  objectives   = 10 pts per O covered (max 30)          -- from CSV O1-O3 flags
  content      = c_count/6 * 20 (max 20)                -- from CSV C1-C6 flags
  cost         = manual 0-15 (free+cert 15 ... Plus-sub 6; -2 access restriction)
  audience_fit = manual 0-15 (gov purpose-built 15, general AI-101 12,
                 partial/niche 9-11, domain-specific 7, grad/technical 6)
  provider     = manual 0-10 (named senior professor top institution 10 ...
                 unnamed team 6-7)
  quality      = manual 0-5 (statewide adoption / >20k+4.6 = 5 ... none 2, mixed 1)
  recency      = 2026:5  2025:4  2024:3
"""
import csv

# name -> (cost, fit, provider, quality, one-line rationale)
M = {
 "AI Foundations for Business Professionals (specialization)": (12,12,10,5,"audit-free; general business AI-101; Holweg (Oxford); 21k+, 4.8/5"),
 "AI Governance": (12,12,10,4,"audit-free; governance module general-professional; Holweg; 12k, 4.8/5"),
 "Foundations of Generative AI": (12,12,9,3,"audit-free (cert $90); general intro; Joyner (GT); new, modest signals"),
 "AI Literacy for Everyone (specialization)": (12,12,7,4,"audit-free; general AI-101; unnamed U-M faculty team; 4.7/539 reviews"),
 "Generative AI: Governance, Policy, and Emerging Regulation": (12,9,9,3,"audit-free; governance-specific + intermediate tag caveat; Hickok (CAIDP)"),
 "AI Fundamentals": (14,12,8,3,"free + free cert route; general intro; Wilson (Leeds)"),
 "Unleash Your Potential: AI Fundamentals": (14,12,9,2,"free; general intro; Bullock (Bristol chair); too new for signals"),
 "Foundation Models and Generative AI (6.S087)": (14,10,7,2,"free, no cert; C1-deep but light workplace fit; researcher-led not professor"),
 "Free Online Certificate in AI and Career Empowerment": (15,13,9,4,"free incl cert; built for transitioning federal workers; Padmanabhan+11; 37k"),
 "GenAI 101": (15,12,8,3,"free incl badge; general workplace skills; Williams (IU)"),
 "AI Whisperer: Crafting Prompts for Generative AI": (14,12,8,3,"free ($39 badge); narrow prompting scope but good on-ramp; Licato (USF)"),
 "Introduction to AI Literacy": (15,12,8,4,"free incl cert; general + strong O2 angle; Lametti; 5k in 2 weeks"),
 "Trustworthy AI: Managing Bias, Ethics, and Accountability": (12,10,8,3,"audit-free; intermediate tag caveat; McCulloh (JHU)"),
 "Artificial Intelligence in National Security": (12,10,9,3,"audit-free (cert $249); natsec niche; Payne (KCL, leading scholar)"),
 "Generative AI Cybersecurity & Privacy for Leaders: A Primer": (12,11,9,4,"audit-free; security niche but leader-framed; White (Vanderbilt); 4.8/5"),
 "AI Literacy for Life & Work": (14,12,8,2,"free (paid cert optional); general; dean-led GVSU; brand new"),
 "AI and Digital Transformation in Government": (15,15,7,5,"free incl cert; purpose-built for civil servants; unnamed Oxford team; 30k/192 countries"),
 "AI, Justice and Rule of Law": (15,9,9,2,"free; justice-domain scope; Cofone (Oxford law); brand new"),
 "Responsible AI for Public Professionals": (15,15,9,5,"free incl cert; purpose-built for public sector; Noveck (Northeastern); statewide mandates NJ/NY/GA/DC"),
 "Responsible AI for Public Organizations": (15,15,9,4,"free incl cert; agency-level gov focus incl NIST AI RMF; Noveck"),
 "Responsible AI for Public Sector Legal Professionals": (15,13,9,3,"free incl cert+CLE; gov but legal-role specific; Noveck + AG association"),
 "A Human Rights-Based Approach to AI": (12,10,8,2,"free but 2025 edition closed (-2); rights-domain; QUB/DIHR/RWI faculty"),
 "AI Safety, Ethics, and Society": (12,10,9,3,"free but application cohort (-2); safety focus; Hendrycks (CAIS) + textbook"),
 "Responsible AI Foundations (course series)": (14,10,8,3,"free (foundation-funded); governance-practitioner scope; Cummings (UVA)"),
 "AI in National Security: Integrating AI into Public Sector Missions": (14,15,8,4,"free; purpose-built federal/natsec; NSCAI-successor practitioners; 6.9k, 4.6/5"),
 "The Future of AI": (14,10,7,3,"free incl cert; trends/safety scope, 2h; team-led nonprofit"),
 "AGI Strategy": (12,9,7,2,"free/PWYW but application cohort (-2); AGI-strategy niche; team-led"),
 "It's Not Just Business - AI Risks Rewards and Responsibilities": (14,10,8,2,"free CC-BY; business-responsibility niche; Jaques/Phillips-Brown (Turing)"),
 "AI Fundamentals for Public Servants": (14,15,8,4,"free; purpose-built for public servants (account restriction aligns with audience, -1); unnamed Stanford HAI faculty; 1.7k gov learners"),
 "The AI Awakening: Implications for the Economy and Society": (6,11,10,4,"Coursera Plus only (no audit); economy/workforce lens; Brynjolfsson (Stanford); 12k, 4.7/5"),
 "The Science and Implications of Generative AI (open archive)": (14,15,10,3,"free CC-BY archive, no cert; purpose-built for public-sector leaders; 3 named HKS professors; no external ratings"),
 "How to AI (Almost) Anything (MAS.S60)": (14,6,9,2,"free OCW; graduate pacing + research component; Liang (MIT Media Lab)"),
 "AI in Education: Leveraging ChatGPT for Teaching": (6,9,10,4,"Coursera Plus only; educator-framed; Mollick (Wharton, leading adoption scholar); 4.8/303, 29k"),
 "Introduction to Generative AI (Duke)": (12,10,8,4,"audit-free; governance-thin, later courses developer-lean; Gift/Deza (Duke MIDS); 30k, 4.5/5"),
 "What Can AI Do for Marketing?": (12,7,9,3,"audit-free; marketing-domain scope; Schweidel (Emory professor)"),
 "Introduction to Artificial Intelligence (UIUC)": (12,12,9,4,"audit-free; general all-six-C intro; Brunner (UIUC assoc dean); 17.5k, 4.7/5"),
 "Introduction to Generative AI (BUSAI X001)": (10,11,8,2,"$49; general non-technical but thin C coverage; Dotson (OSU); new"),
 "Demystifying AI, Understanding Risks, and Shaping the Future": (9,12,8,2,"$99; general non-technical incl risks; Peterson (Purdue); ABET-recognized series"),
 "AI Policy and Governance": (9,13,9,2,"$99; governance for policymakers (gov-relevant); Schiff (Purdue GRAIL, ex-JPMorgan RAI)"),
 "AI Ethics, Inclusion & Society": (14,10,7,2,"free tier; ethics-first, weak O1; senior lecturer + student co-creators (mixed signal)"),
 "Generative AI in Education": (14,7,8,3,"free enrollment; education-domain; Rodolico (Glasgow); 9.5k, 4.6/5"),
 "AI Regulation: Navigating the EU AI Act": (12,8,8,2,"audit-free (cert $140); EU-specific law for US audience; Delft researchers; brand new"),
 "Artificial Intelligence for Everyone (Universiti Malaya)": (14,12,8,2,"free tier/$109; general AI-101; UM AI dept faculty; small enrollment"),
 "Agentic AI and AI Agents: A Primer for Leaders": (12,9,9,5,"audit-free; agentic-AI-specific scope; White (Vanderbilt); 118k, 4.7/5"),
 "Current Issues in Ethics and AI": (6,10,9,2,"Coursera Plus only; ethics/risk-centric; Schnabel (CU Boulder, ex-ACM CEO); new"),
 "AI for Work and Life (UNF)": (12,12,8,2,"free audit (cert $249); explicit AI-101 general design; UNF faculty + guests; new"),
}

REC = {"2024": 3, "2025": 4, "2026": 5}

with open("course_inventory.csv") as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 46, len(rows)

scored = []
for r in rows:
    name = r["course_name"]
    cost, fit, prov, qual, why = M[name]
    c_count = sum(r[c] == "Y" for c in ["C1","C2","C3","C4","C5","C6"])
    o_count = sum(r[o] == "Y" for o in ["O1","O2","O3"])
    obj = o_count * 10
    con = round(c_count / 6 * 20, 1)
    rec = REC[r["year_established"]]
    total = round(obj + con + cost + fit + prov + qual + rec, 1)
    scored.append((total, name, r, dict(o=obj, c=con, cost=cost, fit=fit,
                   prov=prov, qual=qual, rec=rec, c_count=c_count,
                   o_count=o_count, why=why)))

scored.sort(key=lambda x: (-x[0], x[1]))

fields = list(rows[0].keys()) + ["rank","eval_score","o_count","c_count",
    "score_cost","score_audience_fit","score_provider","score_quality","score_recency"]
out = []
for i, (total, name, r, s) in enumerate(scored, 1):
    r2 = dict(r)
    r2.update(rank=i, eval_score=total, o_count=s["o_count"], c_count=s["c_count"],
              score_cost=s["cost"], score_audience_fit=s["fit"],
              score_provider=s["prov"], score_quality=s["qual"],
              score_recency=s["rec"])
    out.append(r2)

# CSV ordered by rank
with open("course_inventory.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out)

# markdown table for evaluation.md
with open("../_cache/cc_ai101_eval_20260716/rank_table.md", "w") as f:
    f.write("| # | Score | Course | Host | O | C | Cost | Fit | Prov | Qual | Rec |\n")
    f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
    for i, (total, name, r, s) in enumerate(scored, 1):
        host = r["host_organization"].split(" (")[0].split(",")[0]
        f.write(f"| {i} | {total} | {name} | {host} | {s['o_count']}/3 | "
                f"{s['c_count']}/6 | {s['cost']} | {s['fit']} | {s['prov']} | "
                f"{s['qual']} | {s['rec']} |\n")
    f.write("\nRationales:\n")
    for i, (total, name, r, s) in enumerate(scored, 1):
        f.write(f"{i}. {name} — {s['why']}\n")
print("Top 12:")
for i, (total, name, r, s) in enumerate(scored[:12], 1):
    print(f"{i:2d} {total:5.1f}  {name}")
print("Bottom 5:")
for i, (total, name, r, s) in enumerate(scored[-5:], len(scored)-4):
    print(f"{i:2d} {total:5.1f}  {name}")
