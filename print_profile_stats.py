#!/usr/bin/env python3

import argparse
import pstats

parser = argparse.ArgumentParser()
parser.add_argument('--file')
parser.add_argument('--limit')
args = parser.parse_args()

file = args.file
limit = int(args.limit)

p = pstats.Stats(file)
p.sort_stats('cumulative').print_stats(limit)
