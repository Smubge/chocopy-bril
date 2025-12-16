#!/usr/bin/env bash
set -e

export DENO_NO_UPDATE_CHECK=1 # Disable Deno update checks if Deno is used somewhere (it was halting the script for some reason???)

# Define paths we use for this script
ROOT=$(cd "$(dirname "$0")/.." && pwd)
COMP="$ROOT/src/main.py"
TEST_DIR="$ROOT/tests"
TMP="$TEST_DIR/tmp.json"

echo "Running differential tests"

for f in "$TEST_DIR"/*.py; do # Iterate over all .py files in the test directory
  base=$(basename "$f") # Get the base filename
  [[ "$base" == "run_diff.sh" ]] && continue # Skip this script itself
  echo "Testing $base" # Print the name of the test file
  py_out=$(python3 "$f") # Run the Python test file and capture its output
  py_out_lc=$(printf '%s' "$py_out" | tr '[:upper:]' '[:lower:]') # convert output to lowercase so True == true

  python3 "$COMP" "$f" > "$TMP" # compile test file with my compiler
  bril_out=$(brili < "$TMP") # run the compiled bril code with brili
  bril_out_lc=$(printf '%s' "$bril_out" | tr '[:upper:]' '[:lower:]')  # lowercase version

  if [[ "$py_out_lc" != "$bril_out_lc" ]]; then  # they should match
    echo "difference found in $base"
    echo "Python:"
    echo "$py_out"
    echo "Bril:"
    echo "$bril_out"
    exit 1
  fi

  echo "Test passed" # Report success for this test
done

rm -f "$TMP" # Clean up temp files
echo "All differential tests passed." # Report overall success

