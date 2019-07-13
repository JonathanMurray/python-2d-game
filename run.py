#!/usr/bin/env python3

import argparse

from pythongame import main

parser = argparse.ArgumentParser()
parser.add_argument('--map')
parser.add_argument('--hero')
args = parser.parse_args()

main.main(args.map, args.hero)
