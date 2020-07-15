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

import hashlib
import os
from pprint import pprint as dataprint
from typing import List

# temporary hardcoding during development
basedir = '~/test'
# blocksize for hashing
blocksize = 65536


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


def get_file_stats(filename: str) -> dict:
    # Return a dict with the size and, if there are multiple links, the inode
    stat_dict = {}
    this_file_stat = os.stat(filename)
    stat_dict['size'] = this_file_stat.st_size
    if this_file_stat.st_nlink > 1:
        stat_dict['inode'] = this_file_stat.st_ino
    return stat_dict


def scan_directory(path: str) -> dict:
    files_dict = {'size': {}, 'inodes': {}}
    for this_path, these_dirs, these_files in os.walk(path, followlinks=False):
        for this_file in these_files:
            this_file_abs_name = this_path + '/' + this_file
            if isfile(this_file_abs_name):
                stats_dict = get_file_stats(this_file_abs_name)
                if not stats_dict['size'] in files_dict['size'].keys():
                    files_dict['size'][stats_dict['size']] = [this_file_abs_name]
                else:
                    files_dict['size'][stats_dict['size']].append(this_file_abs_name)
                if 'inode' in stats_dict.keys():
                    if not stats_dict['inode'] in files_dict['inodes'].keys():
                        files_dict['inodes'][stats_dict['inode']] = [this_file_abs_name]
                    else:
                        files_dict['inodes'][stats_dict['inode']].append(this_file_abs_name)
    return files_dict


def clear_single_entries(stat_sub_dict: dict) -> dict:
    remove_keys = [key for key in stat_sub_dict if len(stat_sub_dict[key]) < 2]
    for this_key in remove_keys:
        stat_sub_dict.pop(this_key)
    return stat_sub_dict


def dict_values_to_list(source_dict: dict) -> List[List[str]]:
    return [source_dict[key] for key in source_dict.keys() if len(source_dict[key]) > 1]


def clean_stat_dict(files_dict: dict) -> dict:
    # clean up the data before returning
    files_dict['size'] = clear_single_entries(files_dict['size'])
    files_dict['inodes'] = dict_values_to_list(files_dict['inodes'])
    return files_dict


def hash_this_file(file_list: List) -> dict:
    file_hashes_dict = {}
    for this_file in file_list:
        hasher = hashlib.sha512()
        with open(this_file,'rb') as read_this_file:
            my_buffer = read_this_file.read(blocksize)
            while len(my_buffer) > 0:
                hasher.update(my_buffer)
                my_buffer = read_this_file.read(blocksize)
        if hasher.hexdigest() not in file_hashes_dict:
            file_hashes_dict[hasher.hexdigest()] = [this_file]
        else:
            file_hashes_dict[hasher.hexdigest()].append(this_file)
    return file_hashes_dict


def get_file_hashes(file_size_dict: dict) -> dict:
    file_hashes_dict = {}
    for this_file in file_size_dict.values():
        file_hashes_dict.update(hash_this_file(this_file))
    return file_hashes_dict


def main(mydir: str) -> None:
    mydir = os.path.expanduser(mydir)  # gets the absolute path if given in a form like ~/mydir
    if isdir(mydir):
        possible_dup_dict = clean_stat_dict(scan_directory(mydir))
        possible_dup_dict['hashes'] = get_file_hashes(possible_dup_dict['size'])
        dataprint(possible_dup_dict)
    else:
        print('{} is not a directory.'.format(mydir))


main(basedir)
