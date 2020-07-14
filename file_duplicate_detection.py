#!/usr/bin/python3
# This came from a live-coding interview which I bombed and decided to use as a learning experience.
# None of this is code from the interview; that was via CoderPad and ended before I could grab a copy.
# From memory of the assignment: given a starting path find duplicate files in that directory and subdirectories.

# outline notes:
# Take starting path
# Find all files.
# Get file size
# Hash files
# Compare hashes

import os, hashlib
from typing import List

# temporary hardcoding during development
basedir = '~/test'

def islink(filename: str) -> bool:
    return os.path.islink(filename)


def isfile(filename: str) -> bool:
    # for this purpose we want to exclude links.
    if not islink(filename):
        return os.path.isfile(filename)
    else:
        return False


def isdir(filename: str) -> bool:
    # for this purpose we want to exclude links.
    if not islink(filename):
        return os.path.isdir(filename)
    else:
        return False


def scandirectory(path: str) -> List['str']:
    pass


def main(basedir: str) -> None:
    basedir = os.path.expanduser(basedir)
    if isdir(basedir):
        print("{} is a directory.".format(basedir))
    else:
        print('{} is not a directory.'.format(basedir))

main(basedir)