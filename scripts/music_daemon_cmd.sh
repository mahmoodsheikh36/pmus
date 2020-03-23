#!/bin/sh

echo -n $@ | nc localhost 5150 | replace_foreign_chars.sh
