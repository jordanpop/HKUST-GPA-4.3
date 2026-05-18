# MCQ Generation Prompt

You are generating exactly 30 multiple-choice questions for one university lecture. Follow every rule below exactly — the output must slot directly into the website JSON without any modification.

---

## Output: one JSON array of 30 question objects

```json
[
  {
    "q": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D", "Option E"],
    "answer": 2,
    "topic": "topic-slug",
    "explain": "Why the correct answer is right. Flag exam traps where relevant. 2–4 sentences.",
    "difficulty": "easy"
  }
]
```

Write the raw JSON array directly to the draft file — no markdown fences, no surrounding text, no comments.

---

## Question rules

- **Exactly 30 questions** — not 29, not 31
- **Exactly 5 options** per question (A through E)
- **`answer`** is 0-based index (0 = A, 1 = B, 2 = C, 3 = D, 4 = E)
- **Vary correct answer position** — distribute correct answers roughly evenly across indices 0–4 across the 30 questions. Aim for 5–7 correct answers at each index. Do not cluster.
- **No duplicates** within the lecture
- **All questions answerable from this lecture only** — do not require knowledge from other lectures
- **Distractors must be plausible** — drawn from related concepts in the same lecture, not obviously wrong
- **Option length parity** — within a single question, all 5 options must be roughly the same length and grammatical form. Do not let the correct option be noticeably longer or more detailed than the distractors. If the correct answer needs explanation, either trim it down to match the distractors OR pad the distractors to match (without making them obviously wrong).
- **Option format parity** — if options are bare nouns or short phrases, ALL 5 must be bare nouns or short phrases. If options are full sentences, ALL 5 must be full sentences. Never mix bare terms with explanatory sentences in the same question.
- **No giveaways via length, specificity, or grammar** — a student should not be able to identify the correct answer purely from option formatting. Reviewer test: cover the question stem and look at the 5 options alone — none should stand out as "the explained one" or "the long one".

---

## Question type mix (across the 30)

Include all of the following types:
- Recall / definition (~8 questions)
- Mechanism / cause-and-effect (~8 questions)
- Comparison / "which is different" (~6 questions)
- "Which is NOT" / exception (~4 questions)
- Application / real-world scenario, case study, or applied problem (~4 questions)
- Process / sequence (~2–4 questions)

Avoid: trivial True/False reworded as MCQ, questions where 3+ options are obviously wrong.

---

## Difficulty distribution (across the 30)

- **easy** — recall / definition: ~10 questions
- **medium** — mechanism / comparison: ~12 questions
- **hard** — application / clinical scenario / multi-step reasoning: ~8 questions

---

## topic-slug rules

- Short kebab-case string matching the `data-topic` attributes in the notes HTML
- Each question must be tagged with the topic of the section it draws from
- Used by the website to group weak areas after quiz — must match notes exactly

---

## Language rules

- Question text: English only
- Options: English only
- Explanations: English; Chinese terms may appear in parentheses if they aid memory
- Use exact terminology from the source PDF

---

## Explanation rules

- 2–4 sentences per explanation
- State why the correct answer is right
- State why the most tempting wrong answer is wrong (flag exam traps)
- Do not repeat the question stem verbatim

---

## JSON correctness rules (CRITICAL)

- Use `\"` to escape any double quotes inside string values
- No trailing commas
- No JavaScript comments inside the JSON
- Validate mentally: every object has all 6 fields (`q`, `options`, `answer`, `topic`, `explain`, `difficulty`)
- `options` must always be an array of exactly 5 strings
