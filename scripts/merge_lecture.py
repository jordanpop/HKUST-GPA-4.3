#!/usr/bin/env python3
"""
merge_lecture.py <subject_code> <lecture_n> [--dry-run]

Merges draft files for one lecture into the website JSON + HTML.
Runs all hard validation checks before touching any production file.

Draft files expected in:
  /Users/winter_08.01/Desktop/GPA4.3 website/prompts/drafts/
    {code}_lec{N}_notes.html
    {code}_lec{N}_questions.json
    {code}_lec{N}_topicmap.json

Production files:
  /Users/winter_08.01/Desktop/GPA4.3 website/HKUST-GPA-4.3/data/{code}.json
  /Users/winter_08.01/Desktop/GPA4.3 website/HKUST-GPA-4.3/{code}.html

Exit 0 + summary on success. Exit 1 + error details on any check failure.
"""

import sys
import json
import re
import os
import math
from pathlib import Path

WEBSITE_ROOT = Path("/Users/winter_08.01/Desktop/GPA4.3 website/HKUST-GPA-4.3")
DRAFTS_DIR = WEBSITE_ROOT / "prompts" / "drafts"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg):
    print(f"WARN: {msg}")


def load_draft_text(path):
    if not path.exists():
        fail(f"Draft file not found: {path}")
    return path.read_text(encoding="utf-8")


def check_notes(html, lecture_n):
    errors = []

    # Must start with correct div
    if not re.search(rf'<div\s+id="notes-{lecture_n}"', html):
        errors.append(f'notes HTML does not contain <div id="notes-{lecture_n}"')

    # Count sections
    sections = re.findall(r'<section\b', html)
    count = len(sections)
    if not (3 <= count <= 8):
        errors.append(f"section count = {count}, expected 3–6 (up to 8 with justification)")

    # data-sec must be integers, not literal "N"
    bad_sec = re.findall(r'data-sec="([^"]*)"', html)
    for val in bad_sec:
        if not val.isdigit():
            errors.append(f'data-sec="{val}" is not an integer')

    # Memorize list item count
    memorize_match = re.search(r'class="memorize[^"]*".*?</div>', html, re.DOTALL)
    if memorize_match:
        items = re.findall(r'<li>', memorize_match.group())
        if not (5 <= len(items) <= 12):
            errors.append(f"memorize list has {len(items)} items, expected 5–12")
    else:
        errors.append("memorize div not found")

    # exam-traps-summary must exist
    if 'class="exam-traps-summary' not in html:
        errors.append("exam-traps-summary div not found")

    # Inline exam-trap divs (separate from summary) — required for in-context warnings
    inline_traps = len(re.findall(r'class="exam-trap(?:-inline)?"', html))
    if inline_traps < 2:
        errors.append(
            f"inline exam-trap divs = {inline_traps}, expected ≥2 (use <div class=\"exam-trap\">…</div> "
            f"in the body where confusion happens; this is separate from the exam-traps-summary block)"
        )

    # Tables — required when 3+ items share attributes (comparisons, parallel structures)
    tables = len(re.findall(r'<table\b', html))
    if tables < 1:
        errors.append(
            f"<table> count = {tables}, expected ≥1 (render 3+ items sharing attributes as a table, not bullets)"
        )

    # SVG diagrams — at least one visual concept graphic per lecture
    svgs = len(re.findall(r'<svg\b', html))
    if svgs < 1:
        errors.append(
            f"<svg> count = {svgs}, expected ≥1 inline SVG diagram (process flow, gradient, or anatomical relationship)"
        )

    # Bullet lists — body must use multiple lists, not one giant list
    body_lists = len(re.findall(r'<(?:ul|ol)\b', html))
    # The memorize <ol> and exam-traps-summary <ul> contribute 2 baseline lists
    if body_lists < 4:
        errors.append(
            f"<ul>/<ol> count = {body_lists}, expected ≥4 (use bullet lists liberally in section bodies, "
            f"not just in memorize / exam-traps-summary)"
        )

    # Chinese annotation density check per section
    section_blocks = re.findall(r'(<section\b.*?</section>)', html, re.DOTALL)
    for i, block in enumerate(section_blocks):
        text_only = re.sub(r'<[^>]+>', ' ', block)
        words = len(text_only.split())
        chinese_count = len(re.findall(r'[一-鿿]', block))
        # count annotation groups (parenthesized Chinese)
        annotations = len(re.findall(r'\([^\)]*[一-鿿][^\)]*\)', block))
        required = math.ceil(words / 80)
        if annotations < required:
            errors.append(
                f"section {i}: {annotations} Chinese annotations, need ≥{required} (word count ~{words})"
            )

    return errors


def check_questions(questions_raw, notes_topics):
    errors = []
    try:
        questions = json.loads(questions_raw)
    except json.JSONDecodeError as e:
        fail(f"questions.json is not valid JSON: {e}")

    if not isinstance(questions, list):
        errors.append("questions.json must be a JSON array")
        return errors, []

    if len(questions) != 30:
        errors.append(f"questions count = {len(questions)}, expected exactly 30")

    required_fields = {"q", "options", "answer", "topic", "explain", "difficulty"}
    valid_difficulties = {"easy", "medium", "hard"}

    answer_tally = [0, 0, 0, 0, 0]

    for i, q in enumerate(questions):
        idx = i + 1
        missing = required_fields - set(q.keys())
        if missing:
            errors.append(f"Q{idx}: missing fields {missing}")
            continue

        if not isinstance(q["options"], list) or len(q["options"]) != 5:
            errors.append(f"Q{idx}: options must be array of exactly 5")

        if not isinstance(q["answer"], int) or not (0 <= q["answer"] <= 4):
            errors.append(f"Q{idx}: answer must be integer 0–4, got {q['answer']!r}")
        else:
            answer_tally[q["answer"]] += 1

        if q["topic"] not in notes_topics:
            errors.append(
                f"Q{idx}: topic '{q['topic']}' not in notes data-topic slugs {sorted(notes_topics)}"
            )

        if q["difficulty"] not in valid_difficulties:
            errors.append(f"Q{idx}: difficulty '{q['difficulty']}' invalid")

    # Answer position distribution check
    for pos, count in enumerate(answer_tally):
        if count < 3 or count > 12:
            warn(f"Answer index {pos} appears {count} times (target 5–7)")

    return errors, questions


def check_topicmap(topicmap_raw, notes_topics):
    errors = []
    try:
        topicmap = json.loads(topicmap_raw)
    except json.JSONDecodeError as e:
        fail(f"topicmap.json is not valid JSON: {e}")

    if not isinstance(topicmap, dict):
        errors.append("topicmap.json must be a JSON object")
        return errors, {}

    # All topicmap keys must be in notes topics
    extra = set(topicmap.keys()) - notes_topics
    if extra:
        errors.append(f"topicmap has keys not in notes data-topic slugs: {extra}")

    return errors, topicmap


def extract_notes_topics(html):
    return set(re.findall(r'data-topic="([^"]+)"', html))


def bump_cache_version(html):
    def increment(m):
        prefix = m.group(1)
        num = int(m.group(2))
        return f"const CACHE = '{prefix}{num + 1}'"

    new_html, count = re.subn(
        r"const CACHE = '([a-zA-Z0-9\-]+?)(\d+)'",
        increment,
        html
    )
    if count == 0:
        warn("Could not find 'const CACHE' version string to bump")
    return new_html


def merge_template_html(html_text, lecture_n, notes_html):
    marker = "<!-- NOTES PAGES go here -->"
    if marker not in html_text:
        fail(f"HTML file does not contain '{marker}'")
    # Strip outer wrapper div if the agent already included it (prevents double-wrapping)
    inner = notes_html.strip()
    outer_open = f'<div id="notes-{lecture_n}" class="page">'
    if inner.startswith(outer_open) and inner.endswith('</div>'):
        inner = inner[len(outer_open):-len('</div>')].strip()
    insert = f'\n<div id="notes-{lecture_n}" class="page">\n{inner}\n</div>\n'
    return html_text.replace(marker, marker + insert, 1)


def merge_hardcoded_html(html_text, lecture_n, lecture_title, notes_html):
    errors = []

    # --- Insertion 1: home card ---
    # Find last lecture card closing </div> inside <div id="home">
    home_match = re.search(r'(<div\s+id="home"[^>]*>)(.*?)(</div>\s*</div>\s*</div>\s*<(?!div\s+id="home"))',
                           html_text, re.DOTALL)
    # Simpler: count existing cards to determine delay class
    card_count = len(re.findall(r'class="card reveal-on-scroll', html_text))
    delay_class = f"reveal-delay-{((card_count) % 3) + 1}"

    card_html = f'''  <div class="card reveal-on-scroll {delay_class}">
    <div class="lec-row">
      <div class="lec-title">{lecture_title}</div>
      <div>
        <button class="btn" onclick="showPage('notes-{lecture_n}')">Notes</button>
        <button class="btn btn-primary" onclick="startQuiz({lecture_n})">Quiz</button>
      </div>
    </div>
    <div class="quiz-settings">
      <label>Questions:
        <select id="count-{lecture_n}"><option value="10">10</option><option value="20">20</option><option value="30" selected>30</option></select>
      </label>
      <span id="status-{lecture_n}" style="color:var(--muted);font-size:.9em"></span>
    </div>
  </div>'''

    # Find last existing card's closing </div> inside home div
    # Strategy: find last occurrence of the card pattern, insert after its closing </div></div>
    last_card_end = None
    for m in re.finditer(r'(<div class="card reveal-on-scroll[^"]*">.*?</div>\s*</div>\s*</div>)', html_text, re.DOTALL):
        last_card_end = m.end()

    if last_card_end is None:
        errors.append("Could not find existing lecture cards in home div")
    else:
        html_text = html_text[:last_card_end] + "\n" + card_html + html_text[last_card_end:]

    if errors:
        fail("\n".join(errors))

    # Recalculate offsets after insertion 1
    # --- Insertion 2: notes div ---
    last_notes_end = None
    for m in re.finditer(r'<div\s+id="notes-\d+"[^>]*class="page"[^>]*>.*?</div>(?=\s*\n\s*<(?:div\s+id="notes-|div\s+id="quiz-|<!--))', html_text, re.DOTALL):
        last_notes_end = m.end()

    # Fallback: just find any notes div end
    if last_notes_end is None:
        for m in re.finditer(r'<div\s+id="notes-\d+"\s+class="page">.*?(?=\n<div\s+id="(?:notes|quiz)-)', html_text, re.DOTALL):
            last_notes_end = m.end()

    if last_notes_end is None:
        fail("Could not find existing notes divs to insert after")

    notes_insert = f'\n{notes_html.strip()}\n'
    html_text = html_text[:last_notes_end] + notes_insert + html_text[last_notes_end:]

    # --- Insertion 3: quiz div ---
    quiz_div = f'''<div id="quiz-{lecture_n}" class="page">
  <a class="btn back" onclick="showPage('home')">&larr; Home</a>
  <div class="score-bar" id="scorebar-{lecture_n}">Score: 0 / 0 (of 30)</div>
  <div id="quizbody-{lecture_n}"></div>
  <div id="postquiz-{lecture_n}"></div>
</div>'''

    last_quiz_end = None
    for m in re.finditer(r'<div\s+id="quiz-\d+"\s+class="page">.*?</div>', html_text, re.DOTALL):
        last_quiz_end = m.end()

    if last_quiz_end is None:
        fail("Could not find existing quiz divs to insert after")

    html_text = html_text[:last_quiz_end] + "\n" + quiz_div + html_text[last_quiz_end:]

    return html_text


def main():
    dry_run = "--dry-run" in sys.argv
    notes_only = "--notes-only" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if len(args) != 2:
        fail("Usage: merge_lecture.py <subject_code> <lecture_n> [--dry-run]")

    code = args[0]
    try:
        lecture_n = int(args[1])
    except ValueError:
        fail(f"lecture_n must be an integer, got {args[1]!r}")

    # Paths
    drafts = DRAFTS_DIR
    notes_path = drafts / f"{code}_lec{lecture_n}_notes.html"
    questions_path = drafts / f"{code}_lec{lecture_n}_questions.json"
    topicmap_path = drafts / f"{code}_lec{lecture_n}_topicmap.json"

    data_json_path = WEBSITE_ROOT / "data" / f"{code}.json"
    html_path = WEBSITE_ROOT / f"{code}.html"

    for p in [data_json_path, html_path]:
        if not p.exists():
            fail(f"Production file not found: {p}")

    # Load drafts
    notes_html = load_draft_text(notes_path)
    if not notes_only:
        questions_raw = load_draft_text(questions_path)
        topicmap_raw = load_draft_text(topicmap_path)

    # --- Validation ---
    print(f"Validating L{lecture_n} drafts for {code}{'  [notes-only]' if notes_only else ''}...")

    notes_errors = check_notes(notes_html, lecture_n)
    notes_topics = extract_notes_topics(notes_html)

    if notes_only:
        questions_errors, questions, topicmap_errors, topicmap = [], [], [], {}
    else:
        questions_errors, questions = check_questions(questions_raw, notes_topics)
        topicmap_errors, topicmap = check_topicmap(topicmap_raw, notes_topics)

        # Subset check: all MCQ topics ⊆ notes topics
        if questions:
            mcq_topics = {q["topic"] for q in questions}
            not_in_notes = mcq_topics - notes_topics
            if not_in_notes:
                questions_errors.append(f"MCQ topics not found in notes: {not_in_notes}")

    all_errors = notes_errors + questions_errors + topicmap_errors
    if all_errors:
        print("\n=== VALIDATION FAILED ===")
        for e in all_errors:
            print(f"  ✗ {e}")
        fail(f"{len(all_errors)} validation error(s). Fix drafts and retry.")

    print(f"  ✓ Notes: {len(re.findall(r'<section', notes_html))} sections, {len(notes_topics)} topics")
    if not notes_only:
        print(f"  ✓ Questions: {len(questions)} questions")
        print(f"  ✓ Topicmap: {len(topicmap)} entries")
        print(f"  ✓ All MCQ topics ⊆ notes data-topic slugs")

    if dry_run:
        print("\nDry run complete — no files modified.")
        return

    # --- Load production files ---
    data = json.loads(data_json_path.read_text(encoding="utf-8"))
    html_text = html_path.read_text(encoding="utf-8")

    # Duplicate lecture check
    existing_ids = {lec["id"] for lec in data.get("lectures", [])}
    if lecture_n in existing_ids:
        fail(f"Lecture {lecture_n} already exists in {data_json_path}. Aborting to prevent duplicate.")

    # --- Update JSON ---
    # Find lecture title from notes HTML h1 (supports "Lecture N:" and "Class N:" prefixes)
    title_match = re.search(rf'<h1>(?:Lecture|Class)\s+\d+:\s*(.*?)</h1>', notes_html)
    lecture_title = title_match.group(1).strip() if title_match else f"Lecture {lecture_n}"

    # Use full h1 text if it starts with "Class N:" pattern, otherwise default "Lecture N: title"
    full_title_match = re.search(r'<h1>(Class\s+\d+:.*?)</h1>', notes_html)
    if full_title_match:
        json_title = full_title_match.group(1).strip()
    else:
        json_title = f"Lecture {lecture_n}: {lecture_title}"

    lecture_obj = {
        "id": lecture_n,
        "title": json_title,
        "questions": questions
    }
    data["lectures"].append(lecture_obj)
    data["topicSectionMap"][str(lecture_n)] = topicmap

    # --- Update HTML ---
    is_template = "renderHomeCards" in html_text

    if is_template:
        html_text = merge_template_html(html_text, lecture_n, notes_html)
    else:
        html_text = merge_hardcoded_html(html_text, lecture_n, lecture_title, notes_html)

    html_text = bump_cache_version(html_text)

    # --- Write production files ---
    data_json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(html_text, encoding="utf-8")

    # --- Delete drafts ---
    draft_paths = [notes_path] if notes_only else [notes_path, questions_path, topicmap_path]
    for p in draft_paths:
        if p.exists():
            p.unlink()
            print(f"  Deleted draft: {p.name}")

    print(f"\n✓ L{lecture_n} merged successfully — {len(questions)} questions, {len(notes_topics)} topics, cache bumped.")


if __name__ == "__main__":
    main()
