# Project Context & Architecture

**Last updated:** 2026-05-15

## Quick Overview
HKUST study guide website with subject selection → lecture → notes/quiz flow.
- **Tech stack:** Pure HTML/CSS/JS, no frameworks, localStorage for progress
- **Data architecture:** Lecture questions live in `data/*.json` and are loaded at runtime via `fetch()`; notes HTML are inlined in subject HTML files
- **Hosted:** https://jordanpop.github.io/HKUST-GPA-4.3/
- **Git rule: NEVER commit or push without explicit user approval**

## File Structure
```
/GPA4.3 website/HKUST-GPA-4.3/   ← git repo root
├── index.html          (homepage: subject selection cards)
├── template.html       (UNIVERSAL TEMPLATE — copy this to start a new subject)
├── 3040.html           (LIFS3040 — UI/logic only)
├── 2921.html           (HUMA2921 — UI/logic only)
├── data/
│   ├── 3040.json       (LIFS3040 lecture data: storageKey, lectures[], topicSectionMap)
│   └── 2921.json       (HUMA2921 lecture data — currently placeholders)
├── CLAUDE.md           (this file)
└── QUESTION_TEMPLATE.md
```

## Navigation Flow
```
index.html → 3040.html or 2921.html → lecture card → notes / quiz
```
Back button on subject pages points to `index.html`.

## Local Preview
The HTML files use `fetch('data/xxxx.json')` and do NOT work over the `file://` protocol. Serve via a local HTTP server:
```bash
cd HKUST-GPA-4.3 && python3 -m http.server 8080
# Open http://localhost:8080/
```
GitHub Pages serves over HTTPS, so production deployment is unaffected.

---

## Data File Schema (`data/{code}.json`)

```json
{
  "storageKey": "endoQuizState",
  "lectures": [
    {
      "id": 1,
      "title": "Lecture 1: ...",
      "questions": [
        {
          "q": "...",
          "options": ["A","B","C","D","E"],
          "answer": 2,
          "topic": "short-topic-name",
          "explain": "...",
          "difficulty": "easy"
        }
      ]
    }
  ],
  "topicSectionMap": {
    "1": { "topic-name": 0, "another-topic": 1 }
  }
}
```

Notes:
- `lectures[].title` is the canonical field (do **not** use `name`)
- `difficulty` is inline on each question (no separate map)
- `topicSectionMap` keys are stringified lecture ids; values map `topic → notes-section-index`

---

## Update Workflow

The canonical workflow is the `/process-pdf-notes` slash command. It handles OCR, spawns notes + MCQ agents in parallel, merges drafts into `data/{code}.json`, bumps the service-worker cache, and pushes. See the skill definition for full details.

Prompt files used by the workflow (all in `prompts/`):
- `notes-agent-template.md` + `notes-agent.md` — notes agent (format rules merged into notes-agent.md)
- `mcq-agent-template.md` + `mcq-agent.md` — MCQ agent (format rules merged into mcq-agent.md)
- `detect-pdf-titles-template.md` — title detection agent

Scripts in `scripts/`:
- `batch_ocr_pdfs.py` — OCR all PDFs in `input/{code}/` to `prompts/drafts/{code}_lec{N}_source.txt`
- `merge_lecture.py` — validate + merge a single lecture's draft into JSON / HTML, bump SW cache, clean drafts

For brand-new subjects: copy `template.html`, replace the five `__PLACEHOLDER__` tokens, create `data/{code}.json` with `{storageKey, lectures: [], topicSectionMap: {}}`, add a card to `index.html`, then run `/process-pdf-notes {code}`.

**Do NOT hand-write the home-page lecture cards, `<div id="notes-N">` blocks, or `<div id="quiz-N">` blocks.** Notes blocks come from the notes agent; quiz containers are rendered at runtime from JSON.

---

## Notes Format (per lecture)

```html
<div class="big-picture">One paragraph framing why this topic matters.</div>

<h2>Section Title</h2>
<p>Plain-English explanation. Technical terms introduced after explanation.</p>
<!-- Tables for comparisons, bold for key terms only -->
<!-- Exam trap inline: <div class="exam-trap">Exam trap: ...</div> -->

<div class="exam-traps-summary">
  <strong>Exam Traps Summary</strong>
  <ul>...</ul>
</div>

<div class="memorize">
  <strong>Top things to memorize</strong>
  <ol>...</ol>
</div>

```

- Add Traditional Chinese terms in parentheses on first mention of each technical term
- Tone: calm, direct, no hype, no em dashes

---

## Question Format (exactly as shown)

```javascript
{
  "q": "Question text?",
  "options": ["A", "B", "C", "D", "E"],
  "answer": 2,
  "explain": "Why correct. Flag exam traps where relevant.",
  "topic": "short-topic-name",
  "difficulty": "easy"
}
```

### Difficulty guide
- **easy** — recall / definition
- **medium** — mechanism / comparison
- **hard** — application / clinical scenario

### Question rules
- Exactly 30 per lecture
- Mix of recall, comparison, application, "which is NOT", cause-and-effect
- Distractors must be plausible (drawn from related concepts)
- Vary correct answer position across the set
- Always append to END of array — never reorder/delete (localStorage uses indices)
- Use proper JSON escaping for quotes inside strings (`\"`)

---

## Balanced Sampling Algorithm
Already implemented in all subject files as `buildBalancedSet(lid, count)`. Distributes across easy/medium/hard proportionally. User selects 10/20/30 via dropdown. Do not modify this function.

## localStorage Keys
| File | Key | Defined in |
|------|-----|------------|
| 3040.html | `endoQuizState` | `data/3040.json` (`storageKey`) |
| 2921.html | `huma2921_quiz_state` | `data/2921.json` (`storageKey`) |

## Service Worker (all subject HTML files)
Every subject HTML registers an inline service worker that caches all GET fetches (including the subject's JSON). When data changes, bump the `CACHE` constant (e.g. `huma2921-v1` → `huma2921-v2`) so old caches are invalidated on next reload. Cache name format: `{subject-slug}-v{N}`. Template already includes this block — new subjects get it automatically.

## CSS Variables (never change)
`--bg, --paper, --ink, --muted, --accent, --accent-soft, --wrong, --wrong-soft, --border`
Font: Georgia / Times New Roman, serif. Beige/green palette. No external libraries.

---

## Content Status
| Subject | File | Notes | Questions |
|---------|------|-------|-----------|
| LIFS2040 | 2040.html + data/2040.json | ✅ Complete (L11–L23, 13 lectures) | ✅ Complete (390 Qs) |
| LIFS3040 | 3040.html + data/3040.json | ✅ Complete (L1–L8, 8 lectures) | ✅ Complete (240 Qs) |
| HUMA2921 | 2921.html + data/2921.json | ✅ Complete (L3–L8, L10, L11 — 8 lectures) | ✅ Complete (240 Qs) |
| MGMT2110 | mgmt2110.html + data/mgmt2110.json | ✅ Complete (Class 11–16, 6 lectures) | ❌ Empty arrays (0 Qs) |
| ISOM2700 | isom2700.html + data/isom2700.json | ✅ Complete (L1–L7, 7 lectures) | ❌ Empty arrays (0 Qs) |
| ISOM2800 | isom2800.html + data/isom2800.json | ✅ Complete (L7–L11, 5 lectures) | ✅ Complete (150 Qs) |

### LIFS3040 Lecture Breakdown
| Lecture | Topic | Source |
|---------|-------|--------|
| L1 | Endo1_2: Endocrine System & Neuroendocrine Systems | Endo1_2-26.pdf |
| L2 | Endo3_4: Metabolic/Developmental Hormones + Water/Electrolyte | Endo3&4-26.pdf |
| L3 | Endo5: Reproductive Hormones | Endo5-26.pdf |
| L4 | GI1: Overview of the Digestive System | GI1-26.pdf |
| L5 | GI2: Digestion — Mouth, Esophagus, Stomach, Pancreas & Liver | GI2-26.pdf |
| L6 | GI3: Absorption — Small Intestine & Large Intestine | GI3-26.pdf |
| L7 | Neuro1: Physiology of Nerve Cells | Neuro1-26.pdf |
| L8 | Neuro2: Properties of Sensory Cells and Sensory Systems | Neuro2-26.pdf |
