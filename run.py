#!/usr/bin/env python3

import argparse

from pythongame import main

parser = argparse.ArgumentParser()
parser.add_argument('--map')
parser.add_argument('--hero')
parser.add_argument('--level')
parser.add_argument('--money')
parser.add_argument('--load')
args = parser.parse_args()

main.main(args.map, args.hero, args.level, args.money, args.load)
