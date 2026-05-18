#!/usr/bin/env bash
# Scaffold a brand-new subject. Copies template.html, fills the five
# __PLACEHOLDER__ tokens, creates data/{code}.json skeleton, creates
# input/{code-folder}/ directory.
#
# Does NOT touch index.html — adding the subject card is manual
# (requires picking an emoji + colour + placement).
#
# Usage:
#   scripts/init_subject.sh <code> "<title>" "<subtitle>" <cache-slug> <storage-key> [<input-folder-name>]
#
# Example:
#   scripts/init_subject.sh 3015 "Cell Biology Study Guide" "Lectures 1-10" lifs3015 lifs3015_quiz_state Lifs3015
set -euo pipefail

if [[ $# -lt 5 ]]; then
  sed -n '2,15p' "$0"
  exit 2
fi

CODE="$1"
TITLE="$2"
SUBTITLE="$3"
CACHE_SLUG="$4"
STORAGE_KEY="$5"
INPUT_DIR="${6:-$CODE}"

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

HTML_OUT="${CODE}.html"
JSON_OUT="data/${CODE}.json"

if [[ -e "$HTML_OUT" ]]; then echo "ERROR: $HTML_OUT already exists"; exit 1; fi
if [[ -e "$JSON_OUT" ]]; then echo "ERROR: $JSON_OUT already exists"; exit 1; fi
if [[ ! -f template.html ]]; then echo "ERROR: template.html missing"; exit 1; fi

cp template.html "$HTML_OUT"

# Use sed with a non-/ delimiter so titles with slashes are safe.
sed -i '' -e "s|__SUBJECT_TITLE__|${TITLE}|g" \
          -e "s|__SUBJECT_CODE__|${CODE}|g" \
          -e "s|__SUBJECT_SUBTITLE__|${SUBTITLE}|g" \
          -e "s|__JSON_NAME__|${CODE}|g" \
          -e "s|__CACHE_NAME__|${CACHE_SLUG}|g" \
          "$HTML_OUT"

# Sanity check: no placeholders left
if grep -q "__[A-Z_]*__" "$HTML_OUT"; then
  echo "ERROR: unfilled placeholders remain in $HTML_OUT:"
  grep -o "__[A-Z_]*__" "$HTML_OUT" | sort -u
  exit 1
fi

mkdir -p data
cat > "$JSON_OUT" <<EOF
{
  "storageKey": "${STORAGE_KEY}",
  "lectures": [],
  "topicSectionMap": {}
}
EOF

mkdir -p "input/${INPUT_DIR}"

# Validate JSON
python3 -c "import json; json.load(open('${JSON_OUT}'))"

echo "Created:"
echo "  ${HTML_OUT}"
echo "  ${JSON_OUT}"
echo "  input/${INPUT_DIR}/"
echo
echo "Next steps:"
echo "  1. Add subject card to index.html (pick emoji + colour)"
echo "  2. Drop PDFs into input/${INPUT_DIR}/"
echo "  3. Run /process-pdf-notes ${CODE}"
