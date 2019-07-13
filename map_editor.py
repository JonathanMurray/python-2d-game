#!/usr/bin/env python3

import argparse

from pythongame import map_editor

parser = argparse.ArgumentParser()
parser.add_argument('--map')
args = parser.parse_args()

map_editor.main(args.map)
