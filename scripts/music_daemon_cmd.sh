#!/bin/sh

echo -n $@ | nc localhost 5150
