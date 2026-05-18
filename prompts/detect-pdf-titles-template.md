# PDF Title Detection Task

For each PDF in the list below, read only the first page (or first visible heading). Return a JSON array — nothing else.

## PDFs to scan

REPLACE_PDF_LIST

## Output format

```json
[
  {
    "file": "/absolute/path/to/file.pdf",
    "detected_title": "Lecture title as it appears on first page",
    "suggested_lecture_n": 7
  }
]
```

Rules:
- `detected_title`: the lecture title text from the first page heading, verbatim
- `suggested_lecture_n`: integer inferred from any "Lecture N" or "L N" text on the first page; null if not found
- Output raw JSON array only, no fences, no surrounding text
