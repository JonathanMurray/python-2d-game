#!/usr/bin/env sh

FILE="resources/sound/$1"

ffmpeg -i "$FILE.wav" "$FILE.ogg"