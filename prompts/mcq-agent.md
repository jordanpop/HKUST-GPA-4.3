# MCQ Agent Instructions

Generate exactly 30 multiple-choice questions in JSON format for one lecture.

Primary source: completed notes HTML only. Do NOT access any PDF.

---

## Step 1 — Read notes and extract topics

1. Read `{{NOTES_DRAFT_PATH}}` — extract all unique `data-topic` slug values from `<p data-topic="...">` and `<div class="exam-trap-inline" data-topic="...">` attributes.
2. These slugs are your authoritative topic list.

Output confirmation: `READ_OK: [list of data-topic slugs found in notes]`

Every MCQ `topic` field must exactly match a `data-topic` value from the notes. No exceptions.

---

## Step 2 — Write 30 questions

Generate exactly 30 multiple-choice questions. Aim for a mix of question types:
- Recall / definition: ~8
- Mechanism / cause-and-effect: ~8
- Comparison / "which is different": ~6
- "Which is NOT" / exception: ~4
- Application / scenario: ~4

Difficulty distribution target: easy ~10, medium ~12, hard ~8.

### JSON structure

```json
{
  "q": "Question text?",
  "options": ["Option A", "Option B", "Option C", "Option D", "Option E"],
  "answer": 2,
  "topic": "topic-slug",
  "explain": "Why correct answer is right. Why the most tempting wrong answer is wrong. 2–4 sentences.",
  "difficulty": "easy"
}
```

### Hard rules

- Exactly 30 questions — not 29, not 31
- Exactly 5 options per question
- `answer` is 0-based index (0 = first option)
- `topic` must be a slug from the notes `data-topic` attributes
- `difficulty` is one of: `"easy"`, `"medium"`, `"hard"`
- No trailing commas, no JS comments, escape internal double quotes with `\"`

### Distractors

Each wrong option must be drawn from related concepts in the same lecture. Must be plausible — a student who studied but hasn't mastered the material might pick it.

### Explanations

2–4 sentences: state why the correct answer is right + why the most tempting wrong answer is wrong. Do not repeat the question stem verbatim.

### Option parity rules

Within a single question, all 5 options must be:
- Roughly the same length
- Same grammatical form (all bare nouns OR all full sentences — never mixed)
- No option should stand out as "the explained one" or "the long one" when the stem is covered

---

## Step 3 — Validation checklist

Before writing the output file, verify:

- [ ] Exactly 30 questions
- [ ] Every question has exactly 5 options
- [ ] All `topic` values are in the notes' data-topic slug list
- [ ] No duplicate question stems
- [ ] JSON syntax valid (all 6 fields per object, no trailing commas)

---

## Step 4 — Write topicSectionMap

Create a JSON object mapping each topic slug to its section number from the notes.

Format — keys are topic slugs, values are 0-indexed `data-sec` integer from the notes:

```json
{"insulin-secretion": 0, "gi-motility": 1, "absorption": 2}
```

One entry per unique topic slug that appears in the 30 questions.

---

## Output

Write raw JSON array (starting with `[`, ending with `]`) to: `{{QUESTIONS_DRAFT_PATH}}`

Write topicSectionMap object to: `{{TOPICMAP_DRAFT_PATH}}`

No markdown fences. No surrounding text.

Return: `L{{LECTURE_N}} MCQ complete — 30 questions, topics: [list]`
