#!/usr/bin/python3
# This came from a live-coding interview which I bombed and decided to use as a learning experience.
# None of this is code from the interview; that was via CoderPad and ended before I could grab a copy.
# From memory of the assignment: given a starting path find duplicate files in that directory and subdirectories.

import hashlib
import os
from collections import defaultdict
from typing import List

# Depending on usage it can be useful to exclude directories that are expected to change rapidly
exclude_dirs = ['.cache', '.config']
# temporary hard coding during development
basedir = '~/'
# blocksize for hashing
blocksize = 65536


def islink(filename: str) -> bool:
    return os.path.islink(filename)


def isfile(filename: str) -> bool:
    # for this purpose we want to exclude symlinks.
    if not islink(filename):
        return os.path.isfile(filename)
    else:
        return False


def isdir(filename: str) -> bool:
    # for this purpose we want to exclude symlinks.
    if not islink(filename):
        return os.path.isdir(filename)
    else:
        return False


def get_file_stats(filename: str) -> dict:
    # Return a dict with the size and, if there are multiple links, the inode
    stat_dict = {}
    this_file_stat = os.stat(filename)
    stat_dict['size'] = this_file_stat.st_size
    if this_file_stat.st_nlink > 1:
        stat_dict['inode'] = this_file_stat.st_ino
    return stat_dict


def scan_directory(path: str) -> dict:
    # Create the combined dict with output from called procedures
    files_dict = {'size': defaultdict(list), 'inodes': defaultdict(list)}
    for this_path, these_dirs, these_files in os.walk(path, topdown=True, followlinks=False):
        these_dirs[:] = [d for d in these_dirs if d not in exclude_dirs]
        for this_file in these_files:
            this_file_abs_name = this_path + '/' + this_file
            if isfile(this_file_abs_name):
                stats_dict = get_file_stats(this_file_abs_name)
                files_dict['size'][stats_dict['size']].append(this_file_abs_name)
                if 'inode' in stats_dict:
                    files_dict['inodes'][stats_dict['inode']].append(this_file_abs_name)
    return files_dict


def clear_single_entries(stat_sub_dict: dict) -> dict:
    # If any keys have single-item lists as values then we don't need to process them
    remove_keys = [key for key in stat_sub_dict if len(stat_sub_dict[key]) < 2]
    for this_key in remove_keys:
        stat_sub_dict.pop(this_key)
    return stat_sub_dict


def dict_values_to_list(source_dict: dict) -> List[List[str]]:
    return [source_dict[key] for key in source_dict if len(source_dict[key]) > 1]


def clean_stat_dict(files_dict: dict) -> dict:
    # clean up the data before returning
    files_dict['size'] = clear_single_entries(files_dict['size'])
    files_dict['inodes'] = dict_values_to_list(files_dict['inodes'])
    return files_dict


def hash_this_file(file_list: List) -> dict:
    file_hashes_dict = defaultdict(list)
    for this_file in file_list:
        if os.access(this_file, os.R_OK):
            with open(this_file, 'rb') as read_this_file:
                hasher = hashlib.sha512()
                my_buffer = read_this_file.read(blocksize)
                while len(my_buffer) > 0:
                    hasher.update(my_buffer)
                    my_buffer = read_this_file.read(blocksize)
                file_hashes_dict[hasher.hexdigest()].append(this_file)
    return file_hashes_dict


def get_file_hashes(file_size_dict: dict) -> dict:
    file_hashes_dict = {}
    for this_file in file_size_dict.values():
        file_hashes_dict.update(hash_this_file(this_file))
    return file_hashes_dict


def main(my_dir: str) -> dict:
    possible_dup_dict = {}
    my_dir = os.path.expanduser(my_dir)  # gets the absolute path if given in a form like ~/my_dir
    if isdir(my_dir):
        possible_dup_dict = clean_stat_dict(scan_directory(my_dir))
        possible_dup_dict['hashes'] = get_file_hashes(possible_dup_dict['size'])
    else:
        print('{} is not a directory.'.format(my_dir))
    return possible_dup_dict


main(basedir)
