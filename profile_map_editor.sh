#!/usr/bin/env sh

echo "Profiling map editor..."

FILENAME=".profile_stats"

python3 -m cProfile -o $FILENAME map_editor.py

echo "Saved profiled stats to $FILENAME"

./print_profile_stats.py --file $FILENAME --limit 10