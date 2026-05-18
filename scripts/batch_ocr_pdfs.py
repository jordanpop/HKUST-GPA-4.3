#!/usr/bin/env python3
"""
batch_ocr_pdfs.py <subject_code>

Auto-OCR all PDFs in input/{SubjectCode}/ → prompts/drafts/{code}_lec{N}_source.txt

Uses ocrmypdf with --skip-text (only OCRs pages without embedded text, fast).
Output: plain UTF-8 text files ready for notes agent.

Exit 0 on success. Exit 1 on any OCR failure.
"""

import sys
import subprocess
import re
from pathlib import Path

WEBSITE_ROOT = Path("/Users/winter_08.01/Desktop/GPA4.3 website/HKUST-GPA-4.3")
INPUT_DIR = WEBSITE_ROOT / "input"
DRAFTS_DIR = WEBSITE_ROOT / "prompts" / "drafts"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        fail("Usage: batch_ocr_pdfs.py <subject_code>")

    code = sys.argv[1].upper()

    # Find subject folder (case-insensitive)
    subject_dir = None
    for folder in INPUT_DIR.iterdir():
        if folder.is_dir() and folder.name.upper() == code:
            subject_dir = folder
            break

    if not subject_dir:
        fail(f"Subject folder not found: {INPUT_DIR / code}")

    # Collect all PDFs
    pdfs = sorted(subject_dir.glob("*.pdf"))
    if not pdfs:
        fail(f"No PDFs found in {subject_dir}")

    print(f"Found {len(pdfs)} PDF(s) in {subject_dir.name}")

    # Ensure drafts dir exists
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    # OCR each PDF
    for pdf_path in pdfs:
        # Extract lecture number from filename.
        # Patterns supported:
        #   "L1.pdf", "GI2-26.pdf", "LIFS2040-2026 Lecture 15.pdf"  → explicit L/Lecture prefix
        #   "08-Forecasting-2.pdf", "10-Inventory.pdf"               → leading number + dash/space
        match = (
            re.search(r'(?:[Ll]ecture\s+|[Ll])(\d+)', pdf_path.stem)
            or re.match(r'^(\d+)[^0-9]', pdf_path.stem)
        )
        if not match:
            print(f"⚠ Skipping {pdf_path.name} — cannot detect lecture number")
            continue

        lec_num = match.group(1)
        output_txt = DRAFTS_DIR / f"{code.lower()}_lec{lec_num}_source.txt"

        print(f"  OCRing L{lec_num}...", end=" ", flush=True)

        try:
            result = subprocess.run(
                [
                    "ocrmypdf",
                    "--sidecar", str(output_txt),
                    "--force-ocr",
                    str(pdf_path),
                    "/dev/null"
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(f"FAILED")
                print(f"    stderr: {result.stderr}")
                fail(f"ocrmypdf failed on {pdf_path.name}")

            # Verify output exists and has content
            if not output_txt.exists():
                print(f"FAILED")
                fail(f"ocrmypdf did not create {output_txt.name}")

            size_kb = output_txt.stat().st_size / 1024
            print(f"✓ ({size_kb:.1f} KB)")

        except subprocess.TimeoutExpired:
            print(f"TIMEOUT")
            fail(f"ocrmypdf timeout on {pdf_path.name}")
        except Exception as e:
            print(f"ERROR")
            fail(f"ocrmypdf error on {pdf_path.name}: {e}")

    print(f"\n✓ OCR complete — all .txt files ready in {DRAFTS_DIR.name}")


if __name__ == "__main__":
    main()
