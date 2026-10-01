#!/usr/bin/env bash
set -u
repo=$1
artifacts=$2
cat_bin=$3
index=0
for relative in src/a src/b; do
  "$cat_bin" -- "$repo/$relative" > "$artifacts/$index.stdout" 2> "$artifacts/$index.stderr"
  code=$?
  printf "%s\n" "$code" > "$artifacts/$index.status"
  index=$((index + 1))
done
