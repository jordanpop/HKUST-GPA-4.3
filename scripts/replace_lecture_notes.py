#!/usr/bin/env python3
"""
Replace one lecture's notes block in {code}.html with the draft at
prompts/drafts/{code}_lec{N}_notes.html. Rebuilds topicSectionMap[N]
from data-sec / data-topic markers in the new notes, bumps the
service-worker cache version, validates JSON, deletes drafts.

With --with-mcq, ALSO replaces lectures[i].questions with the array in
prompts/drafts/{code}_lec{N}_questions.json. The question file must be a
JSON array of 30 question objects. topicSectionMap is taken from the
notes draft, not from the topicmap draft.

Usage:
    python3 scripts/replace_lecture_notes.py <code> <N> [<N> ...]
    python3 scripts/replace_lecture_notes.py <code> <N> [<N> ...] --with-mcq
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def extract_topic_section_map(notes_html: str) -> dict:
    out: dict[str, int] = {}
    parts = re.split(r'(<section[^>]*data-sec="\d+"[^>]*>)', notes_html)
    current = None
    sec_pat = re.compile(r'data-sec="(\d+)"')
    topic_pat = re.compile(r'data-topic="([^"]+)"')
    for chunk in parts:
        m = sec_pat.search(chunk) if chunk.startswith("<section") else None
        if m:
            current = int(m.group(1))
            continue
        if current is None:
            continue
        for slug in topic_pat.findall(chunk):
            out.setdefault(slug, current)
    return out


def replace_one(html: str, n: int, draft: str) -> str:
    open_tag = f'<div id="notes-{n}" class="page">'
    next_open = f'<div id="notes-{n + 1}" class="page">'
    next_quiz = '<div id="quiz-1" class="page">'

    start = html.find(open_tag)
    if start < 0:
        raise SystemExit(f"L{n}: opening tag not found in HTML")

    # Find the boundary: prefer next notes-{n+1}, fall back to quiz-1
    boundary = html.find(next_open, start + 1)
    if boundary < 0:
        boundary = html.find(next_quiz, start + 1)
    if boundary < 0:
        raise SystemExit(f"L{n}: cannot locate end of block")

    # Walk back to just after the matching </div>\n (preserve the blank line gap)
    block_end = html.rfind("</div>", start, boundary)
    if block_end < 0:
        raise SystemExit(f"L{n}: closing </div> not found")
    block_end += len("</div>")
    # Include the trailing newline if present
    if block_end < len(html) and html[block_end] == "\n":
        block_end += 1

    draft = draft.rstrip() + "\n"
    return html[:start] + draft + html[block_end:]


def bump_cache(html: str) -> str:
    def repl(m):
        slug, n = m.group(1), int(m.group(2))
        return f"const CACHE = '{slug}-v{n + 1}';"
    new_html, count = re.subn(
        r"const CACHE = '([a-z0-9-]+?)-v(\d+)';", repl, html, count=1
    )
    if count != 1:
        raise SystemExit("cache bump: marker not found")
    return new_html


def main(argv: list[str]) -> int:
    args = argv[1:]
    with_mcq = "--with-mcq" in args
    args = [a for a in args if a != "--with-mcq"]
    if len(args) < 2:
        print(__doc__)
        return 2
    code = args[0]
    lectures = sorted({int(x) for x in args[1:]})

    html_path = ROOT / f"{code}.html"
    json_path = ROOT / f"data/{code}.json"
    drafts_dir = ROOT / "prompts/drafts"

    if not html_path.exists():
        raise SystemExit(f"{html_path} not found")
    if not json_path.exists():
        raise SystemExit(f"{json_path} not found")

    html = html_path.read_text()
    data = json.loads(json_path.read_text())
    data.setdefault("topicSectionMap", {})
    lecture_by_id = {L["id"]: L for L in data["lectures"]}

    drafts_to_delete: list[pathlib.Path] = []
    for n in lectures:
        draft_path = drafts_dir / f"{code}_lec{n}_notes.html"
        if not draft_path.exists():
            raise SystemExit(f"draft missing: {draft_path}")
        draft = draft_path.read_text()
        if f'<div id="notes-{n}"' not in draft:
            raise SystemExit(
                f"L{n}: draft must start with <div id=\"notes-{n}\" class=\"page\">"
            )
        html = replace_one(html, n, draft)
        tmap = extract_topic_section_map(draft)
        if not tmap:
            raise SystemExit(f"L{n}: no data-topic slugs found in draft")
        data["topicSectionMap"][str(n)] = tmap
        drafts_to_delete.append(draft_path)

        mcq_info = ""
        if with_mcq:
            q_path = drafts_dir / f"{code}_lec{n}_questions.json"
            if not q_path.exists():
                raise SystemExit(f"questions draft missing: {q_path}")
            questions = json.loads(q_path.read_text())
            if not isinstance(questions, list) or len(questions) != 30:
                raise SystemExit(
                    f"L{n}: questions must be a JSON array of exactly 30 items "
                    f"(got {type(questions).__name__} len={len(questions) if isinstance(questions, list) else 'n/a'})"
                )
            for i, q in enumerate(questions):
                for key in ("q", "options", "answer", "explain", "topic", "difficulty"):
                    if key not in q:
                        raise SystemExit(f"L{n} Q{i+1}: missing field '{key}'")
                if not isinstance(q["options"], list) or len(q["options"]) != 5:
                    raise SystemExit(f"L{n} Q{i+1}: options must be array of 5")
            if n not in lecture_by_id:
                raise SystemExit(f"L{n}: lecture id not found in JSON")
            lecture_by_id[n]["questions"] = questions
            drafts_to_delete.append(q_path)
            tm_path = drafts_dir / f"{code}_lec{n}_topicmap.json"
            if tm_path.exists():
                drafts_to_delete.append(tm_path)
            mcq_info = ", MCQ replaced (30 Q)"

        print(f"  L{n}: replaced notes block, {len(tmap)} topic slugs{mcq_info}")

    html = bump_cache(html)

    html_path.write_text(html)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    # Validate JSON round-trip
    json.loads(json_path.read_text())

    for p in drafts_to_delete:
        p.unlink()

    cache_match = re.search(r"const CACHE = '([^']+)';", html)
    print(f"Cache bumped to: {cache_match.group(1) if cache_match else '?'}")
    print(f"Updated: {html_path.name}, data/{code}.json")
    print(f"Deleted {len(drafts_to_delete)} draft file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
