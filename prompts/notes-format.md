# Notes Generation Prompt

You are generating structured study notes for one university lecture. Follow every rule below exactly — the output must slot directly into the website without any modification.

---

## HARD REQUIREMENTS — your output MUST contain

Before writing the file, plan each item below. After writing, **self-count each one**. If any is 0 (or below the minimum), rewrite the relevant section before saving — the merge script rejects drafts that fail these checks.

- [ ] **Sections**: 3–6 `<section>` blocks (up to 8 only with strong justification)
- [ ] `data-sec="N"` on every section, where N is an **integer** (not the literal letter N)
- [ ] **Tables**: ≥1 `<table>` block. Any time 3+ items share the same attributes (source, signal, function, location, etc.), render as a table — never as a bullet list.
- [ ] **Inline exam traps**: ≥2 `<div class="exam-trap">…</div>` placed in the body **where the confusion happens**. These are separate from and in addition to the final summary block.
- [ ] **Exam traps summary**: exactly 1 `<div class="exam-traps-summary">` at the end, listing all traps in one place.
- [ ] **SVG diagram**: ≥1 inline `<svg>` showing a process flow, gradient, anatomical relationship, or comparison. No external image files. Use simple shapes, arrows, labels.
- [ ] **Bullet lists**: ≥5 total `<ul>` / `<ol>` blocks across the document. Don't lump everything into one giant list.
- [ ] **Memorize block**: `<div class="memorize"><ol>` with 5–12 `<li>` items.
- [ ] **Lower-yield block**: `<div class="lower-yield">` listing skip-if-short-on-time items.
- [ ] **Traditional Chinese (繁體)** annotation in parentheses on first mention of each technical term. Density: roughly 1 annotation per 80 words per section.

### Bad vs Good examples

❌ **BAD** — 3 parallel items rendered as bullets:
```html
<ul>
  <li>Acid stimulus 1: gastrin from G cells, hormonal signal</li>
  <li>Acid stimulus 2: histamine from ECL cells, paracrine signal</li>
  <li>Acid stimulus 3: acetylcholine from vagus, neural signal</li>
</ul>
```

✅ **GOOD** — same content as a table:
```html
<table>
  <tr><th>Stimulus</th><th>Source cell</th><th>Signal type</th></tr>
  <tr><td>Gastrin</td><td>G cells</td><td>Hormonal</td></tr>
  <tr><td>Histamine</td><td>ECL cells</td><td>Paracrine</td></tr>
  <tr><td>Acetylcholine</td><td>Vagus nerve</td><td>Neural</td></tr>
</table>
```

❌ **BAD** — only a summary, no inline warnings:
```html
<!-- (body has no <div class="exam-trap"> at all) -->
<div class="exam-traps-summary"><ul><li>...</li></ul></div>
```

✅ **GOOD** — inline warning right where the confusion is, AND a summary at the end:
```html
<p>Tight junctions seal cells together at the apical membrane…</p>
<div class="exam-trap">Exam trap: tight junctions ≠ desmosomes. Tight junctions seal; desmosomes anchor.</div>
<p>(continue explaining)…</p>
<!-- ... -->
<div class="exam-traps-summary"><strong>Exam Traps Summary</strong><ul>…</ul></div>
```

---

## Output: one complete `<div id="notes-N">` block

Replace N with the confirmed lecture number. The block must follow this structure character-for-character:

```html
<div id="notes-N" class="page">
  <a class="btn back" onclick="showPage('home')">← Home</a>
  <button id="clear-hl-N" class="btn btn-danger" style="display:none;float:right" onclick="clearWeakHighlights(N)">Clear Highlights</button>
  <h1>Lecture N: [Title]</h1>

  <div class="bigpic reveal-on-scroll">
    [One paragraph framing the topic. Maximum 4 sentences. Prefer 3. Cover only: what the lecture is about, why it matters, and the key throughline. Do not summarise individual sections. Prose only, no bullet points.]
  </div>

  <section class="reveal-on-scroll" data-sec="0">
    <h2>1. [Section Title]</h2>
    <p data-topic="topic-slug">[Plain-English explanation first. Technical term introduced after. Bold sparingly — key terms only. Chinese term in parentheses on first mention within this section.]</p>
    <!-- tables for side-by-side comparisons -->
    <div class="exam-trap-inline" data-topic="topic-slug"><b>Exam trap:</b> [trap text]</div>
  </section>

  <section class="reveal-on-scroll" data-sec="1">
    <h2>2. [Section Title]</h2>
    [content]
  </section>

  <section class="reveal-on-scroll" data-sec="2">
    <h2>3. [Section Title]</h2>
    [content]
  </section>

  <!-- Continue for each section. data-sec is a real integer starting at 0, incrementing by 1.
       Replace the literal character "N" — never write data-sec="N" in the output.
       3–6 sections total. -->

  <div class="exam-traps-summary reveal-on-scroll reveal-delay-1">
    <strong>Exam Traps Summary</strong>
    <ul>
      <li>[Every exam trap from this lecture collected here, one line each]</li>
    </ul>
  </div>

  <div class="memorize reveal-on-scroll reveal-delay-2">
    <strong>Top things to memorize</strong>
    <ol>
      <li>[Minimum 5 items, maximum ~12, ranked by importance]</li>
    </ol>
  </div>
</div>
```

---

## Structure rules (non-negotiable)

- `bigpic` div comes first, before any `<section>`
- Each content section = one `<section class="reveal-on-scroll" data-sec="N">`, N starts at 0
- Inline exam traps (`exam-trap-inline`) go inside the relevant `<section>` right after the content they relate to
- `exam-traps-summary` and `memorize` are always **outside** all `<section>` tags, at the bottom, in that order
- Every content element that maps to a quiz topic MUST have `data-topic="topic-slug"` matching the `topic` field in the MCQ questions
- `exam-traps-summary` is MANDATORY — never omit, even if there are few traps
- `memorize` list minimum 5 items
- 3–6 sections per lecture (not fewer, not more unless PDF genuinely requires it)

---

## Content rules

- **Content completeness (non-negotiable):** Cover ALL content from this PDF. Do not omit any point, even minor details, sub-bullets, side notes, captions, or examples. You MAY condense filler, repetition, or verbose phrasing into tighter wording, but the underlying information must all be preserved. If in doubt whether to include something, include it. Follow the PDF's original structure and topic ordering exactly. Do not move topics to other lectures.
- **Big picture paragraph:** Maximum 4 sentences. Prefer 3. Cover only: what the lecture is about, why it matters, and the key throughline. Do not summarise individual sections. Prose only, no lists.
- **Bullet-first format:** Within sections, use bullet points as the default format. Reserve prose only for: (a) the bigpic paragraph, and (b) short sequential flows (e.g. swallowing reflex steps) where numbered lists work better. Avoid restating bullet content in surrounding prose. Tables remain preferred for side-by-side comparisons.
- **Each section:** Plain-English explanation first, technical term after. Bold sparingly (key terms only, not whole phrases)
- **Chinese annotations (繁體中文):** Add Traditional Chinese in parentheses generously, not just for the headline academic term. Three cases require Chinese:
  (a) Every subject-specific or technical term on first mention per section (e.g. marginal cost 邊際成本, photosynthesis 光合作用, deontology 義務論).
  (b) Inside explanations of a technical term, any English word that is itself non-trivial or could trip up a non-native reader (e.g. when explaining a concept, words like "threshold" 閾值, "aggregate" 總和, "coefficient" 係數, "permeable" 可通過的 should also get Chinese if they appear).
  (c) Common-but-ambiguous English words used in a specific technical sense (e.g. "potential" meaning 電位 not 潛力, "function" meaning 函數 not 功能).
  Err on the side of more Chinese, not less. Skip Chinese only for basic everyday English.
- **Tables:** Use liberally for side-by-side comparisons (hormone classes, receptor types, parallel structures)
- **Exam traps:** Must appear both inline inside the relevant `<section>` AND collected in `exam-traps-summary`
- **Visual concept graphics:** Where a process, gradient, anatomical relationship, or comparison would be clearer as a visual than as text, add an inline HTML/SVG visual concept graphic (NOT an image file). Use simple shapes, arrows, labels, and CSS — no external assets. Examples of good candidates: HCl secretion transporter diagram on parietal cell membrane, bile flow path from hepatocytes to duodenum, three-stimuli convergence onto H⁺/K⁺-ATPase, swallowing reflex sequence. Skip if a table or bullet list already conveys the relationship cleanly. Aim for 1–3 such visuals per lecture, only where they genuinely add clarity.
- **Reference style (gold standard — match these exactly):** The following style properties are derived from the Lecture 5 GI2 reference output and apply to all future lectures:
  - **Bullet density:** Target ≥90% of section content in bullet points. A section with 6 sub-items (e.g. cell types, roles, components) should have 6 bullets, not 1 prose paragraph listing them.
  - **Bullet sentence length:** Each bullet is one dense fact-sentence — typically one line, two at most. Format: `term (Chinese) — mechanism/function; specific value if available`. Never pad.
  - **Specificity:** Always give exact numbers and values where the PDF provides them (e.g. "~1.5 L/day", "pH < 5", "pH ~2", "~50% of world population"). Never replace a specific figure with a vague qualifier like "a large amount" or "most".
  - **Uniform depth:** Every concept, cell type, enzyme, or mechanism receives the same level of detail regardless of perceived exam importance. Minor cells (e.g. ECL cells) are treated with the same depth as major ones (e.g. parietal cells). Do not thin out coverage for items that seem secondary.
  - **Tables for parallel structures:** Whenever the PDF presents 3+ items that share the same attributes (source, signal type, function), render them as a table, not a bullet list. See: three acid stimuli table, gastric gland cells table, pancreatic enzyme classes table.
  - **No prose restatement of bullets:** Do not open or close a bullet group with a prose sentence that restates what the bullets already say (e.g. "There are four roles of saliva:" is acceptable as a lead-in; restating those four roles again in a closing sentence is not).
- **Tone:** Calm, direct, no hype, no em dashes

---

## topic-slug rules

- Short kebab-case string, e.g. `insulin-secretion`, `divine-command`, `gi-motility`
- Must match exactly what will be used in the MCQ `topic` field
- Used by the website to highlight weak areas after quiz — consistency is critical
