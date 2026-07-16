# Courses Candidates

This folder collects researched **free or low-cost courses** that teach people **AI 101** — foundational, beginner-friendly artificial intelligence education.

## Purpose

Serve as a curated staging area for candidate courses to be evaluated and potentially recommended for AI upskilling. Each candidate entry should capture enough detail to compare courses and decide which ones to promote.

## What Belongs Here

- Introductory AI / machine learning courses (no or minimal prerequisites)
- Free courses, or low-cost ones (roughly under $100, or with free-audit options)
- Offerings from MOOCs (Coursera, edX, Udacity), universities, vendors (Google, Microsoft, AWS, IBM, Anthropic, OpenAI), nonprofits, and government training programs

## Suggested Entry Format

Add one Markdown file per course (or per provider), including:

| Field | Description |
|---|---|
| Course name | Official title |
| Provider | Platform and/or institution |
| URL | Link to the course page |
| Cost | Free / audit-free / price; certificate cost if any |
| Duration | Estimated hours or weeks |
| Prerequisites | Expected background (ideally none for AI 101) |
| Format | Self-paced, cohort, video, hands-on labs, etc. |
| Topics covered | Key subjects (e.g., ML basics, neural networks, generative AI, ethics) |
| Certificate | Whether a completion certificate is offered |
| Notes | Quality signals, reviews, last-updated date, accessibility |

## Contents

- `concepts.md` — canonical concept map (82 concepts, C1–C6 × O1–O3) anchoring the search
- `courses.md` — 46 verified course candidates (28 from pass 1 + 18 from the gap-analysis pass) with full details, deduplicated near-misses, and an unverified watch-list
- `course_inventory.csv` — machine-readable course-to-C/O mapping with host, fee, instructor, program, notes; sorted by rank with evaluation-score columns
- `evaluation.md` — scoring methodology, full ranking of the 46, tier analysis, recommended pathway, sensitivity notes
- `plans/` — concept search plan and course search plan (methodology)
- `backups/` — pre-change file backups

## Status

- [x] Initial research pass (2026-07-16: 6 concept agents + 7 course-track agents + 3 QA agents)
- [x] Candidate entries added (28 eligible, 2024+ launches, professor/non-profit-led, free or ≤$150)
- [x] Gap-analysis pass over elite/flagship universities (2026-07-16: 6 gap tracks + 2 QA agents → +18 courses, total 46)
- [x] Evaluation and shortlisting (2026-07-16: rubric-scored ranking of all 46; Tier-1 shortlist of 7; see evaluation.md)
