# Project Context & Architecture

**Last updated:** 2026-05-15

## Quick Overview
HKUST study guide website with subject selection → lecture → notes/quiz flow.
- **Tech stack:** Pure HTML/CSS/JS, no frameworks, localStorage for progress
- **Hosted:** https://jordanpop.github.io/HKUST-GPA-4.3/
- **Git rule: NEVER commit or push without explicit user approval**

## File Structure
```
/GPA4.3 website/HKUST-GPA-4.3/   ← git repo root
├── index.html          (homepage: subject selection cards)
├── 3040.html           (LIFS3040 — Lectures 1–5)
├── 2921.html           (HUMA2921 — Lectures 3, 4, 5)
├── CLAUDE.md           (this file)
└── QUESTION_TEMPLATE.md
```

## Navigation Flow
```
index.html → 3040.html or 2921.html → lecture card → notes / quiz
```
Back button on subject pages points to `index.html`.

---

## Update Workflow (follow this every time)

### Case 1: Adding a new lecture to an existing subject
User drops PDF/PPTX → say which subject and lecture number

Steps:
1. Read `CLAUDE.md` only (do not re-read the full HTML)
2. Read only the target HTML file's `const lectures = [` array to check existing lecture IDs
3. Generate notes HTML using the Notes Format below
4. Generate exactly 30 questions using the Question Format below
5. Inject into the target HTML:
   - Add lecture card to home page section
   - Add notes div (`notes-N`)
   - Add quiz div (`quiz-N`)
   - Add entry to `const lectures = [...]`
   - Add entry to `const quizState = {...}`
6. Ask user to approve before committing

### Case 2: Adding a new subject
User drops PDF/PPTX for a new course

Steps:
1. Create a new HTML file (copy 2921.html as template)
2. Update localStorage key to `[COURSECODE]QuizState`
3. Update `const lectures = [...]` with correct lecture ids/names
4. Add a new subject card to `index.html`
5. Update this CLAUDE.md content status table
6. Ask user to approve before committing

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
  q: "Question text?",
  options: ["A", "B", "C", "D", "E"],  // always exactly 5 options
  answer: 2,                             // 0-indexed (0–4)
  explain: "Why correct. Flag exam traps where relevant.",
  topic: "short-topic-name",
  difficulty: "easy" | "medium" | "hard"
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
- Use double quotes for strings containing apostrophes (e.g. `"You've"` not `'You've'`)

---

## Balanced Sampling Algorithm
Already implemented in all subject files. `getBalancedSample(questions, total)` distributes across easy/medium/hard proportionally. User selects 10/20/30 via dropdown. Do not modify this function.

## localStorage Keys
| File | Key |
|------|-----|
| 3040.html | `3040QuizState` |
| 2921.html | `2921QuizState` |

## CSS Variables (never change)
`--bg, --paper, --ink, --muted, --accent, --accent-soft, --wrong, --wrong-soft, --border`
Font: Georgia / Times New Roman, serif. Beige/green palette. No external libraries.

---

## Content Status
| Subject | File | Notes | Questions |
|---------|------|-------|-----------|
| LIFS3040 | 3040.html | ✅ Complete (L1–L10) | ✅ Complete |
| HUMA2921 | 2921.html | 🚧 Placeholder (L3,4,5) | 🚧 Empty arrays |

### LIFS3040 Lecture Breakdown
| Lecture | Topic | Source |
|---------|-------|--------|
| L1–L5 | Endocrine System | Endo1_2-26.pdf, Endo3&4-26.pdf, Endo5-26.pdf |
| L6 | GI Overview & Upper GI | GI1-26.pdf |
| L7 | Small Intestine & Absorption | GI2-26.pdf |
| L8 | Large Intestine, Liver & Pancreas | GI3-26.pdf |
| L9 | Neurons, Glia & Membrane Potentials | Neuro1-26.pdf |
| L10 | Synaptic Transmission & Neural Circuits | Neuro2-26.pdf |
