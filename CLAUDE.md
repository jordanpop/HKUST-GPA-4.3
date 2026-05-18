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

## Update Workflow (follow this every time)

### Case 1: Adding a new lecture to an existing subject
User drops PDF/PPTX → say which subject and lecture number

Steps:
1. **Scan the actual PDF structure** — read through the PDF to identify the real topics, sections, and ordering. Do NOT rely on CLAUDE.md's lecture breakdown table (it may be stale or incorrect).
2. Confirm with user: "This PDF covers [topics in actual order], right?" — get explicit confirmation before proceeding.
3. Open `data/{code}.json` to check existing lecture IDs
4. **Generate exactly 30 questions** using the Question Format below (all questions must be answerable from this lecture's PDF only)
5. **Generate notes HTML** using the Notes Format below, following the PDF's actual structure exactly
6. **Update only `data/{code}.json`**: append the new lecture object (with all 30 questions) and any new topic→section mappings. The fetch-based architecture means you do NOT edit the HTML file for data updates.
7. **If this is the first lecture:** You will need to add a `<div id="notes-N">` and `<div id="quiz-N">` block to the HTML file once. After that, only JSON updates are needed.
8. Update CLAUDE.md's reference table only after confirming the PDF structure matches
9. Ask user to approve before committing

### Case 2: Adding a new subject
User drops PDF/PPTX for a new course.

**ALWAYS start from `template.html`. Never copy an existing subject HTML — they may have drifted.**

Steps:
1. `cp template.html {code}.html` (e.g. `cp template.html 3015.html`)
2. In the new file, find-and-replace these five placeholders:
   - `__SUBJECT_TITLE__` — display title (e.g. `Endocrine Study Guide`)
   - `__SUBJECT_CODE__` — course code (e.g. `LIFS3040`)
   - `__SUBJECT_SUBTITLE__` — short scope description (e.g. `Lectures 1-10`)
   - `__JSON_NAME__` — JSON file basename (e.g. `3040` → `data/3040.json`). Appears TWICE.
   - `__CACHE_NAME__` — service-worker cache namespace (e.g. `lifs3040`)
3. Create `data/{code}.json` with the schema described below. Set `storageKey` to something unique (e.g. `lifs3040_quiz_state`).
4. **SCAN the actual PDF structure** — read through each PDF to identify the real topics, sections, and ordering. Do NOT rely on file names alone. Confirm with user: "This lecture covers [topics in actual order], right?" — get explicit confirmation before proceeding.
5. **Spawn agents for parallel processing:**
   - **Agent 1 (Notes Generator):** Reads the PDF and `prompts/notes-format.md`, then generates the complete notes HTML block (`<div id="notes-N">...</div>`) for this lecture. Follow the Content completeness rule: cover ALL content from the PDF.
   - **Agent 2 (MCQ Generator):** Reads the PDF and `prompts/mcq-format.md`, then generates exactly 30 multiple-choice questions in JSON format. Must include option length/format parity rules and balanced answer position distribution.
   - Both agents work in parallel. Do NOT wait for one to finish before starting the other.
6. Once both agents complete, collect their outputs:
   - Insert the notes HTML block into the new subject HTML file at the location marked `NOTES PAGES go here`
   - Parse the JSON questions and append to `data/{code}.json` under the correct lecture object, along with updated `topicSectionMap`
7. Add a new subject card to `index.html`.
8. Update this CLAUDE.md Content Status table.
9. Ask user to approve before committing.

**Do NOT hand-write the home-page lecture cards or `<div id="quiz-N">` blocks.** They are generated at runtime by `renderHomeCards()` / `renderQuizContainers()` from the JSON data. Hand-writing them will cause duplicates.

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

<div class="lower-yield">
  <strong>Lower-yield / skip if short on time</strong>
  <ul>...</ul>
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
| LIFS3040 | 3040.html + data/3040.json | ✅ Complete (L1–L10) | ✅ Complete (300 Qs) |
| HUMA2921 | 2921.html + data/2921.json | 🚧 Placeholder (L3,4,5) | 🚧 Empty arrays |

### LIFS3040 Lecture Breakdown
| Lecture | Topic | Source |
|---------|-------|--------|
| L1–L5 | Endocrine System | Endo1_2-26.pdf, Endo3&4-26.pdf, Endo5-26.pdf |
| L6 | GI Overview & Upper GI | GI1-26.pdf |
| L7 | GI Digestion — Pancreas & Liver | GI2-26.pdf |
| L8 | GI Absorption — Small & Large Intestine | GI3-26.pdf |
| L9 | Neurons, Glia & Membrane Potentials | Neuro1-26.pdf |
| L10 | Synaptic Transmission & Neural Circuits | Neuro2-26.pdf |
