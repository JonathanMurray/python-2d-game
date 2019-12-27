#!/usr/bin/env sh

echo "Profiling game..."

FILENAME=".profile_stats"

python3 -m cProfile -o $FILENAME run.py

echo "Saved profiled stats to $FILENAME"

./print_profile_stats.py --file $FILENAME --limit 10