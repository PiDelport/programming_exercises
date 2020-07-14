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
from pprint import pprint as dataprint

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


def GetFileStats(filename: str) -> dict:
    # Return a dict with the size and, if there are multiple links, the inode
    stat_dict = {}
    this_file_stat = os.stat(filename)
    stat_dict['size'] = this_file_stat.st_size
    if this_file_stat.st_nlink > 1:
        stat_dict['inode'] = this_file_stat.st_ino
    return stat_dict


def ScanDirectory(path: str) -> dict:
    files_dict = { 'size': {}, 'inodes': {}}
    for this_path, these_dirs, these_files in os.walk(path, followlinks=False):
        for this_file in these_files:
            this_file_abs_name = this_path + '/' + this_file
            if isfile(this_file_abs_name):
                stats_dict = GetFileStats(this_file_abs_name)
                if not stats_dict['size'] in files_dict['size'].keys():
                    files_dict['size'][stats_dict['size']] = [this_file_abs_name]
                else:
                    files_dict['size'][stats_dict['size']].append(this_file_abs_name)
                if 'inode' in files_dict.keys():
                    if not stats_dict['inode'] in files_dict['inodes'].keys():
                        files_dict['inodes'][stats_dict['inode']] = [this_file_abs_name]
                    else:
                        files_dict['inodes'][stats_dict['inode']].append(this_file_abs_name)
    return files_dict


def main(basedir: str) -> None:
    basedir = os.path.expanduser(basedir) # gets the absolute path if given in a form like ~/mydir
    if isdir(basedir):
        possible_dup_dict = ScanDirectory(basedir)
        dataprint(possible_dup_dict)
    else:
        print('{} is not a directory.'.format(basedir))

main(basedir)