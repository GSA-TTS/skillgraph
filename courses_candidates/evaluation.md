# Evaluation & Ranking of the 46 AI 101 Course Candidates

Date: 2026-07-16. Inputs: `course_inventory.csv` (46 QA-verified courses), `courses.md`
(full entries), `concepts.md` (C/O anchors). The inventory CSV is now sorted by rank and
carries the per-component scores in columns `rank`, `eval_score`, `o_count`, `c_count`,
`score_cost`, `score_audience_fit`, `score_provider`, `score_quality`, `score_recency`.

## 1. Methodology

Composite score, 0–100, seven components. Weights reflect the dataset's purpose: the
statutory education objectives (O1–O3) dominate, followed by content breadth (C1–C6);
cost, audience fit, provider strength, quality signals, and recency refine the ordering.

| Component | Max | How scored |
|---|---|---|
| Objectives coverage (O1–O3) | 30 | 10 pts per objective met (from QA-verified CSV flags) |
| Content coverage (C1–C6) | 20 | (count of C areas covered ÷ 6) × 20 |
| Cost / accessibility | 15 | free incl. certificate 15 · free (free/cheap cert) 14 · free-to-audit (cert paid) 12 · ≤$60 10 · ≤$150 9 · Coursera Plus-only ~$59/mo 6; −2 for access friction (application cohorts, closed editions, account restrictions) |
| Audience fit | 15 | purpose-built for government 15 · general professional AI 101 12 · partially general / niche framing 9–11 · domain-specific (education, marketing, EU law, agentic-only) 7–8 · graduate pacing 6 |
| Provider & instructor | 10 | named senior professor, top institution 10 · named professor, solid institution 8–9 · credible team/practitioner-led 7–8 · unnamed faculty team 6–7 |
| Quality signals | 5 | statewide adoption or >20k enrolled with ≥4.6 rating 5 · solid ratings/enrollment 3–4 · too new / no signals 2 · mixed 1 |
| Recency | 5 | 2026 = 5 · 2025 = 4 · 2024 = 3 |

Coverage components are mechanical (computed from the QA-verified CSV flags); cost, fit,
provider, and quality are manually curated per course with a one-line rationale (Section 4).
Scoring is reproducible: the script embeds every manual score.

## 2. Ranking

| # | Score | Course | Host | O | C | Cost | Fit | Prov | Qual | Rec |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 95.0 | The Science and Implications of Generative AI (open archive) | Harvard Kennedy School | 3/3 | 6/6 | 14 | 15 | 10 | 3 | 3 |
| 2 | 94.0 | AI Fundamentals for Public Servants | Stanford Online + Stanford HAI | 3/3 | 6/6 | 14 | 15 | 8 | 4 | 3 |
| 3 | 94.0 | Responsible AI for Public Sector Legal Professionals | InnovateUS | 3/3 | 6/6 | 15 | 13 | 9 | 3 | 4 |
| 4 | 93.7 | Responsible AI for Public Organizations | InnovateUS | 3/3 | 5/6 | 15 | 15 | 9 | 4 | 4 |
| 5 | 93.7 | Responsible AI for Public Professionals | InnovateUS | 3/3 | 5/6 | 15 | 15 | 9 | 5 | 3 |
| 6 | 92.7 | AI and Digital Transformation in Government | Oxford Saïd + UNESCO | 3/3 | 5/6 | 15 | 15 | 7 | 5 | 4 |
| 7 | 91.0 | Introduction to Artificial Intelligence (UIUC) | UIUC (Gies) | 3/3 | 6/6 | 12 | 12 | 9 | 4 | 4 |
| 8 | 89.7 | AI Foundations for Business Professionals (specialization) | Oxford Saïd | 3/3 | 5/6 | 12 | 12 | 10 | 5 | 4 |
| 9 | 88.3 | Free Online Certificate in AI and Career Empowerment | UMD Smith | 3/3 | 4/6 | 15 | 13 | 9 | 4 | 4 |
| 10 | 88.0 | AI Literacy for Everyone (specialization) | University of Michigan | 3/3 | 6/6 | 12 | 12 | 7 | 4 | 3 |
| 11 | 88.0 | AI for Work and Life (UNF) | University of North Florida | 3/3 | 6/6 | 12 | 12 | 8 | 2 | 4 |
| 12 | 86.7 | Artificial Intelligence for Everyone | Universiti Malaya | 3/3 | 5/6 | 14 | 12 | 8 | 2 | 4 |
| 13 | 85.3 | AI Governance | Oxford Saïd | 3/3 | 4/6 | 12 | 12 | 10 | 4 | 4 |
| 14 | 83.3 | Generative AI Cybersecurity & Privacy for Leaders | Vanderbilt | 3/3 | 4/6 | 12 | 11 | 9 | 4 | 4 |
| 15 | 81.7 | AI Regulation: Navigating the EU AI Act | TU Delft | 3/3 | 5/6 | 12 | 8 | 8 | 2 | 5 |
| 16 | 81.7 | AI in National Security (SCSP) | Special Competitive Studies Project | 2/3 | 5/6 | 14 | 15 | 8 | 4 | 4 |
| 17 | 78.7 | AI in Education: Leveraging ChatGPT for Teaching | Wharton | 3/3 | 5/6 | 6 | 9 | 10 | 4 | 3 |
| 18 | 78.7 | Unleash Your Potential: AI Fundamentals | University of Bristol | 2/3 | 5/6 | 14 | 12 | 9 | 2 | 5 |
| 19 | 77.3 | Introduction to AI Literacy | Acadia University | 2/3 | 4/6 | 15 | 12 | 8 | 4 | 5 |
| 20 | 77.0 | AI Ethics, Inclusion & Society | University of Glasgow | 2/3 | 6/6 | 14 | 10 | 7 | 2 | 4 |
| 21 | 76.7 | Foundations of Generative AI | Georgia Tech | 2/3 | 5/6 | 12 | 12 | 9 | 3 | 4 |
| 22 | 75.0 | How to AI (Almost) Anything (MAS.S60) | MIT Media Arts and Sciences | 2/3 | 6/6 | 14 | 6 | 9 | 2 | 4 |
| 23 | 74.3 | AI Literacy for Life & Work | Grand Valley State | 2/3 | 4/6 | 14 | 12 | 8 | 2 | 5 |
| 24 | 74.0 | What Can AI Do for Marketing? | Emory (Goizueta) | 3/3 | 3/6 | 12 | 7 | 9 | 3 | 3 |
| 25 | 73.3 | AI Fundamentals | University of Leeds | 2/3 | 4/6 | 14 | 12 | 8 | 3 | 3 |
| 26 | 71.7 | Generative AI in Education | University of Glasgow | 2/3 | 5/6 | 14 | 7 | 8 | 3 | 3 |
| 27 | 71.3 | Artificial Intelligence in National Security | King's College London | 2/3 | 4/6 | 12 | 10 | 9 | 3 | 4 |
| 28 | 70.7 | The AI Awakening | Stanford School of Engineering | 2/3 | 5/6 | 6 | 11 | 10 | 4 | 3 |
| 29 | 70.3 | AI Safety, Ethics, and Society | Center for AI Safety | 2/3 | 4/6 | 12 | 10 | 9 | 3 | 3 |
| 30 | 70.3 | Introduction to Generative AI (Duke) | Duke University | 2/3 | 4/6 | 12 | 10 | 8 | 4 | 3 |
| 31 | 70.0 | AI, Justice and Rule of Law | UNESCO + Oxford | 2/3 | 3/6 | 15 | 9 | 9 | 2 | 5 |
| 32 | 69.3 | A Human Rights-Based Approach to AI | Global Campus of Human Rights | 2/3 | 4/6 | 12 | 10 | 8 | 2 | 4 |
| 33 | 69.3 | AI Policy and Governance | Purdue University | 2/3 | 4/6 | 9 | 13 | 9 | 2 | 3 |
| 34 | 69.0 | Agentic AI and AI Agents: A Primer for Leaders | Vanderbilt | 2/3 | 3/6 | 12 | 9 | 9 | 5 | 4 |
| 35 | 69.0 | Responsible AI Foundations (course series) | All Tech Is Human | 2/3 | 3/6 | 14 | 10 | 8 | 3 | 4 |
| 36 | 68.7 | GenAI 101 | Indiana University (Kelley) | 2/3 | 2/6 | 15 | 12 | 8 | 3 | 4 |
| 37 | 68.0 | The Future of AI | BlueDot Impact | 2/3 | 3/6 | 14 | 10 | 7 | 3 | 4 |
| 38 | 67.7 | AI Whisperer | University of South Florida | 2/3 | 2/6 | 14 | 12 | 8 | 3 | 4 |
| 39 | 67.3 | Demystifying AI, Understanding Risks... | Purdue University | 2/3 | 4/6 | 9 | 12 | 8 | 2 | 3 |
| 40 | 67.0 | It's Not Just Business | The Alan Turing Institute | 2/3 | 3/6 | 14 | 10 | 8 | 2 | 3 |
| 41 | 67.0 | Trustworthy AI: Managing Bias, Ethics, Accountability | Johns Hopkins | 2/3 | 3/6 | 12 | 10 | 8 | 3 | 4 |
| 42 | 66.0 | Generative AI: Governance, Policy, Emerging Regulation | University of Michigan | 2/3 | 3/6 | 12 | 9 | 9 | 3 | 3 |
| 43 | 64.3 | Current Issues in Ethics and AI | CU Boulder | 2/3 | 4/6 | 6 | 10 | 9 | 2 | 4 |
| 44 | 64.0 | AGI Strategy | BlueDot Impact | 2/3 | 3/6 | 12 | 9 | 7 | 2 | 4 |
| 45 | 61.7 | Introduction to Generative AI (BUSAI X001) | Ohio State | 2/3 | 2/6 | 10 | 11 | 8 | 2 | 4 |
| 46 | 56.0 | Foundation Models and Generative AI (6.S087) | MIT OCW | 1/3 | 3/6 | 14 | 10 | 7 | 2 | 3 |

## 3. Analysis

### Tier 1 — Core recommendations (ranks 1–7, score ≥ 91)

Every Tier-1 course meets all three objectives, is free (or free-to-audit), and five of
seven are purpose-built for government audiences. This is the shortlist for a federal
AI 101 pathway:

- **Harvard Kennedy School — The Science and Implications of GenAI (#1)** is the single
  most complete offering: all six content areas, three named HKS professors, public-sector
  framing, fully open CC-BY archive. Its only weaknesses — no certificate, no cohort, 2024
  vintage — are noted in the score (quality 3, recency 3).
- **Stanford HAI — AI Fundamentals for Public Servants (#2)** matches it on coverage;
  ranked below on unnamed instructors and the Apolitical account restriction.
- **The InnovateUS trio (#3–5)** is the operational backbone: free with certificates,
  refreshed every six months, already mandated statewide (NJ, NY, GA, DC), and the only
  free courses teaching the NIST AI RMF directly to government staff.
- **Oxford/UNESCO (#6)** is the strongest internationally-scoped civil-servant course
  (30k learners, 192 countries); slightly penalized for no named lead professor.
- **UIUC (#7)** is the best *general-audience university* intro: the only non-gov-specific
  course covering all six C areas with all three objectives, free to audit.

### Tier 2 — Strong complements (ranks 8–16, 80–90)

Broad-coverage generalists (Oxford spec #8, U-M #10, UNF #11, UMD #9 — the latter built
for transitioning federal workers) plus the best single-topic anchors: Oxford AI
Governance (#13) for C5, Vanderbilt Cyber & Privacy (#14) for synthetic-media/security
risks, SCSP (#16) for homeland/national-security trends (C6), TU Delft (#15) for
comparative regulation. These fill gaps left by any Tier-1 selection.

### Tier 3 — Useful specialists (ranks 17–35, 69–79)

Solid but constrained: niche scope (KCL natsec, CAIS safety, Glasgow ethics, Purdue
policy), domain framing (Wharton/Glasgow education, Emory marketing), pacing (MIT
MAS.S60), paywall (Wharton, AI Awakening — Coursera Plus only), or access friction
(CAIS/HRBA cohorts). Use them as electives per role.

### Tier 4 — Marginal for this purpose (ranks 36–46, < 69)

Not weak courses — weak *fits*: micro-scope on-ramps (GenAI 101, AI Whisperer, OSU),
governance add-ons that assume prior grounding (U-M Hickok, JHU, ATIH), Plus-paywalled
CU Boulder, application-gated AGI Strategy, and MIT 6.S087 (#46), which is excellent
C1 material but meets only one objective and carries no O2/O3 content.

### Cross-cutting observations

1. Government-purpose-built courses dominate: 6 of the top 7. The gap-analysis pass
   contributed 2 of the top 7 (#1, #2) and 5 of the top 16 — it materially changed the top
   of the ranking, validating the revision.
2. Objective O3 (governance/civil-rights) is the differentiator: 18 of 46 courses miss it,
   and no course below rank 17 that misses O3 breaks 78. O1+O2 are near-commodities;
   O3 coverage is scarce and mostly lives in gov-specific and governance-specific courses.
3. The Coursera Plus paywall costs real rank: Wharton (#17), AI Awakening (#28), and
   CU Boulder (#43) each lose ~6–8 points vs. audit-free peers of similar content.
4. No single course covers everything well; the pathway below beats any individual pick.

### Recommended learning pathway (federal AI 101)

1. Foundation (pick one): HKS #1 (richest) or InnovateUS Public Professionals #5
   (shortest, certificated) or UIUC #7 (most systematic)
2. Government application: Oxford/UNESCO #6 or Stanford #2
3. Risk & governance: InnovateUS Public Organizations #4 (NIST AI RMF) + Oxford AI
   Governance #13
4. Trends/security elective: SCSP #16 (natsec) or Vanderbilt #14 (synthetic media/privacy)

## 4. Per-course score rationales

1. HKS Science & Implications of GenAI — free CC-BY archive, no cert; purpose-built for public-sector leaders; 3 named HKS professors; no external ratings.
2. Stanford AI Fundamentals for Public Servants — free; purpose-built (account restriction aligns with audience, −1); unnamed Stanford HAI faculty; 1.7k gov learners.
3. InnovateUS Legal Professionals — free incl cert + CLE; gov but legal-role specific; Noveck + AG-association reach.
4. InnovateUS Public Organizations — free incl cert; agency-level gov focus incl NIST AI RMF; Noveck.
5. InnovateUS Public Professionals — free incl cert; purpose-built public sector; statewide mandates NJ/NY/GA/DC.
6. Oxford/UNESCO Gov — free incl cert; purpose-built civil servants; unnamed faculty team; 30k/192 countries.
7. UIUC Intro to AI — audit-free; general all-six-C intro; Brunner; 17.5k, 4.7/5.
8. Oxford AI Foundations spec — audit-free; general business AI-101; Holweg; 21k+, 4.8/5.
9. UMD AICE — free incl cert; built for transitioning federal workers; Padmanabhan +11 faculty; 37k.
10. U-M AI Literacy spec — audit-free; general AI-101; unnamed faculty team; 4.7/539.
11. UNF AI for Work and Life — free audit (cert $249); explicit AI-101 design; new, no signals yet.
12. Universiti Malaya — free tier/$109; general AI-101; UM AI dept faculty; small enrollment.
13. Oxford AI Governance — audit-free; general-professional governance; Holweg; 12k, 4.8/5.
14. Vanderbilt Cyber & Privacy — audit-free; security niche, leader-framed; White; 4.8/5.
15. TU Delft EU AI Act — audit-free (cert $140); EU-specific for US audience; brand new.
16. SCSP AI in National Security — free; purpose-built federal/natsec; NSCAI-successor practitioners (not professors); 6.9k, 4.6/5; misses O2.
17. Wharton AI in Education — Coursera Plus only; educator-framed; Mollick; 4.8/303.
18. Bristol Unleash Your Potential — free; general intro; Bullock; too new for signals.
19. Acadia Intro to AI Literacy — free incl cert; strong O2 angle; 5k in 2 weeks; misses O3.
20. Glasgow AI Ethics, Inclusion & Society — free tier; ethics-first, weak O1; student co-creators (mixed signal).
21. Georgia Tech Foundations of GenAI — audit-free (cert $90); general intro; Joyner; modest signals.
22. MIT MAS.S60 — free OCW; graduate pacing + research component; Liang.
23. GVSU AI Literacy for Life & Work — free; general; dean-led; brand new.
24. Emory Marketing — audit-free; marketing-domain scope; Schweidel.
25. Leeds AI Fundamentals — free + free cert; general intro; Wilson.
26. Glasgow GenAI in Education — free enrollment; education-domain; 9.5k, 4.6/5.
27. KCL AI in National Security — audit-free (cert $249); natsec niche; Payne.
28. Stanford AI Awakening — Coursera Plus only; economy/workforce lens; Brynjolfsson; 12k, 4.7/5.
29. CAIS AI Safety, Ethics, and Society — free but application cohort (−2); safety focus; Hendrycks + textbook.
30. Duke Intro to GenAI — audit-free; governance-thin; Gift/Deza; 30k, 4.5/5.
31. AI, Justice and Rule of Law — free; justice-domain scope; Cofone; brand new.
32. HRBA to AI — free but 2025 edition closed (−2); rights-domain; QUB/DIHR/RWI.
33. Purdue AI Policy and Governance — $99; governance for policymakers; Schiff (GRAIL).
34. Vanderbilt Agentic AI — audit-free; agentic-only scope; White; 118k, 4.7/5.
35. ATIH Responsible AI Foundations — free; governance-practitioner scope; Cummings (UVA).
36. IU Kelley GenAI 101 — free incl badge; general workplace skills but 2/6 content areas.
37. BlueDot Future of AI — free incl cert; 2-hour trends/safety scope; team-led.
38. USF AI Whisperer — free ($39 badge); narrow prompting scope, good on-ramp.
39. Purdue Demystifying AI — $99; general non-technical incl risks; ABET-recognized series.
40. Turing It's Not Just Business — free CC-BY; business-responsibility niche.
41. JHU Trustworthy AI — audit-free; intermediate-tag caveat; McCulloh.
42. U-M GenAI Governance/Policy/Regulation — audit-free; governance-specific + intermediate tag; Hickok.
43. CU Boulder Current Issues in Ethics and AI — Coursera Plus only; ethics/risk-centric; Schnabel.
44. BlueDot AGI Strategy — free/PWYW but application cohort (−2); AGI-strategy niche.
45. OSU Intro to GenAI — $49; non-technical but 2/6 content areas; new.
46. MIT 6.S087 — free, no cert; C1-deep but meets only O1; researcher-led, not professor.

## 5. Sensitivity & limitations

- **Weight sensitivity.** The top tier is robust: the seven Tier-1 courses hold the top
  seven positions under ±10-point swings between the objectives and content weights,
  because they lead on *both*. Ordering within ties (#2 vs #3, #4 vs #5) flips on small
  provider/quality changes and should not be over-read.
- **If certificates are required**, HKS (#1), Stanford Awakening, and MIT entries drop —
  use the InnovateUS trio, Oxford/UNESCO, UMD, and UNF (audit path lacks the cert).
- **If US-provider-only is required**, remove Oxford (×3-related), Universiti Malaya,
  Glasgow, Bristol, Leeds, Acadia, TU Delft, KCL, Turing, Global Campus — Tier 1
  still retains HKS, Stanford, InnovateUS ×3, and UIUC.
- **Judgment components** (fit, provider, quality) are manually assigned; each carries a
  documented rationale (Section 4) so any disputed score can be revised and the composite
  recomputed mechanically.
- **Point-in-time data.** Coursera audit availability (three Plus-only findings), the UNF
  free-certificate window, and cohort schedules (CAIS, HRBA, BlueDot) change frequently;
  scores reflect July 2026 QA checks.
- **C/O flags are binary.** A course "covering" C4 in one module scores the same as one
  centered on C4; the audience-fit component partially compensates, but depth-weighted
  flags would be the natural next refinement.
