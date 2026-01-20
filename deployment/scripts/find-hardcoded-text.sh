#!/bin/bash

# Script to find hardcoded English text in React components
# This helps identify text that needs translation

echo "=== Finding hardcoded text in React components ==="
echo ""

# Find text in JSX elements (between > and <)
echo "1. Text in JSX elements:"
grep -r -n ">[A-Z][a-zA-Z ]*<" frontend/src/pages/*.tsx frontend/src/components/*.tsx 2>/dev/null | \
  grep -v "className" | \
  grep -v "import" | \
  head -20

echo ""
echo "2. Button text:"
grep -r -n "<Button[^>]*>[A-Z]" frontend/src/pages/*.tsx frontend/src/components/*.tsx 2>/dev/null | head -20

echo ""
echo "3. Heading text:"
grep -r -n "<h[1-6][^>]*>[A-Z]" frontend/src/pages/*.tsx frontend/src/components/*.tsx 2>/dev/null | head -20

echo ""
echo "4. Placeholder text:"
grep -r -n 'placeholder="[A-Z]' frontend/src/pages/*.tsx frontend/src/components/*.tsx 2>/dev/null | head -20

echo ""
echo "5. Title attributes:"
grep -r -n 'title="[A-Z]' frontend/src/pages/*.tsx frontend/src/components/*.tsx 2>/dev/null | head -20

echo ""
echo "=== Done ==="
echo "Review the output above and replace hardcoded text with t('key') calls"
