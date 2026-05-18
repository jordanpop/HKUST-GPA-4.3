# Notes Agent Instructions

Generate a complete, production-ready notes HTML block for one lecture.

---

## Single-pass workflow

Read the source text (extracted via OCRmyPDF from the lecture PDF). Write notes HTML directly.

### HTML structure (follow character-for-character)

```html
<div id="notes-{{LECTURE_N}}" class="page">
  <a class="btn back" onclick="showPage('home')">← Home</a>
  <button id="clear-hl-{{LECTURE_N}}" class="btn btn-danger" style="display:none;float:right" onclick="clearWeakHighlights({{LECTURE_N}})">Clear Highlights</button>
  <h1>Lecture {{LECTURE_N}}: {{LECTURE_TITLE}}</h1>

  <div class="bigpic reveal-on-scroll">
    [3–4 sentences. What this lecture is about, why it matters, key throughline. Prose only, no lists.]
  </div>

  <section class="reveal-on-scroll" data-sec="0">
    <h2>1. [Section Title]</h2>
    <p data-topic="topic-slug">[content]</p>
    <div class="exam-trap-inline" data-topic="topic-slug"><b>Exam trap:</b> [trap text]</div>
  </section>

  <!-- Repeat sections. data-sec is a real integer (0, 1, 2...). 3–6 sections total. -->

  <div class="exam-traps-summary reveal-on-scroll reveal-delay-1">
    <strong>Exam Traps Summary</strong>
    <ul>
      <li>[every trap from this lecture, one line each]</li>
    </ul>
  </div>

  <div class="memorize reveal-on-scroll reveal-delay-2">
    <strong>Top things to memorize</strong>
    <ol>
      <li>[5–12 items, ranked by importance]</li>
    </ol>
  </div>
</div>
```

### Structure rules

- `bigpic` comes before all `<section>` tags
- `data-sec` starts at 0, increments by 1 — never write `data-sec="N"` literally
- Inline exam traps go inside the relevant `<section>`, after the content they relate to
- `exam-traps-summary` and `memorize` are outside all `<section>` tags, at the bottom, in that order
- `exam-traps-summary` is mandatory — never omit
- `memorize` minimum 5 items, maximum 12
- 3–6 sections (use up to 8 only if source genuinely requires it)

### Content rules

- **Completeness:** Cover all major topics in the source. After writing each section, verify you've addressed the main ideas.
- **Bullet density:** ≥90% of section content in bullet points. Reserve prose for bigpic and short sequential flows.
- **Bullet format:** `term (中文) — mechanism/function; exact value if available`. One dense fact-sentence per bullet, two lines max. Never pad.
- **Specificity:** Exact numbers from source (e.g. "~1.5 L/day", "pH < 5"). Never replace with vague qualifiers.
- **Uniform depth:** Every concept, cell type, enzyme, mechanism gets the same detail level regardless of perceived exam importance.
- **Tables:** Use for 3+ items sharing the same attributes (source, signal type, function). Prefer tables over bullet lists for parallel structures.
- **No prose restatement of bullets:** Don't open or close bullet groups with a sentence restating what the bullets say.
- **Visuals:** 1–3 inline HTML/SVG concept graphics per lecture where a process or comparison would be clearer visually than as text. No external assets.
- **Tone:** Calm, direct, no hype, no em dashes.

### Chinese annotation rules

Add Traditional Chinese (繁體中文) in parentheses in three cases:
- (a) Every subject-specific or technical term on first mention per section
- (b) Non-trivial English words inside technical explanations (e.g. "threshold" 閾值, "aggregate" 總和, "permeable" 可通過的)
- (c) Common English words used in a specific technical sense (e.g. "potential" meaning 電位)

Aim for roughly one annotation per 80 words. If a section has very few annotations, add more. If it seems overly annotated, trim.

### topic-slug rules

- Short kebab-case: `insulin-secretion`, `gi-motility`, `divine-command`
- Every `<p>` and `<div class="exam-trap-inline">` that maps to a quiz topic must have `data-topic="topic-slug"`
- Use consistent slugs throughout — the MCQ agent will extract these to build the question bank

---

## Hard checks before finalizing

- `<section>` count ∈ [3, 6] (or up to 8 with justification)
- `memorize` item count ∈ [5, 12]
- `data-sec` values are integers starting from 0
- All major topics from the source are addressed in a section
- No `data-sec="N"` literal in output
- `exam-traps-summary` is present
- No markdown fences in output

---

## Output

Write raw HTML block (starting with `<div id="notes-{{LECTURE_N}}"` and ending with `</div>`) to: `{{NOTES_DRAFT_PATH}}`

No markdown fences. No explanatory text outside the HTML block.

Return: `L{{LECTURE_N}} notes complete — [X] sections, topics: [list of data-topic slugs]`
