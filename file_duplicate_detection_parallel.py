#!/usr/bin/python3
# This came from a live-coding interview which I bombed and decided to use as a learning experience.
# None of this is code from the interview; that was via CoderPad and ended before I could grab a copy.
# From memory of the assignment: given a starting path find duplicate files in that directory and subdirectories.

import hashlib
import os
from typing import List
from multiprocessing import Pool

# Depending on usage it can be useful to exclude directories that are expected to change rapidly
exclude_dirs = ['.cache', '.config']
# temporary hardcoding during development
basedir = '~/'
# blocksize for hashing
blocksize = 65536
# Hash algorithm desired
hash_algo = 'sha512'
# Number of parallel threads/processes for hashing
parallel = 8


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
    # Return a dict with the filename, size and, if there are multiple links, the hardlinks
    stat_dict = {'filename': filename}
    this_file_stat = os.stat(filename)
    stat_dict['size'] = this_file_stat.st_size
    if this_file_stat.st_nlink > 1:
        stat_dict['hardlinks'] = this_file_stat.st_ino
    return stat_dict


def generate_file_list(path: str) -> List[str]:
    files_list = []
    for this_path, these_dirs, these_files in os.walk(path, followlinks=False):
        these_dirs[:] = [d for d in these_dirs if d not in exclude_dirs]
        for this_file in these_files:
            if isfile(this_path + '/' + this_file):
                files_list.append(this_path + '/' + this_file)
    return files_list


def concatonate_stat_dicts(stat_dict_list: List[dict]) -> dict:
    return_stats_dict = {'size': {}, 'hardlinks': {}}
    for this_file_dict in stat_dict_list:
        if this_file_dict['size'] in return_stats_dict['size']:
            return_stats_dict['size'][this_file_dict['size']].append(this_file_dict['filename'])
        else:
            return_stats_dict['size'][this_file_dict['size']] = [this_file_dict['filename']]
        if 'hardlinks' in this_file_dict:
            if this_file_dict['hardlinks'] in return_stats_dict['hardlinks']:
                return_stats_dict['hardlinks'][this_file_dict['hardlinks']].append(this_file_dict['filename'])
            else:
                return_stats_dict['hardlinks'][this_file_dict['hardlinks']] = [this_file_dict['filename']]
    return return_stats_dict


def run_file_stats(file_list: List[str]) -> dict:
    stats_pool = Pool(processes=parallel)
    file_stats_list = stats_pool.map(get_file_stats, file_list)
    return concatonate_stat_dicts(file_stats_list)


def scan_directory(path: str) -> dict:
    files_list = generate_file_list(path)
    files_dict = run_file_stats(files_list)
    return files_dict


def clear_single_entries(sub_dict: dict) -> dict:
    remove_keys = [key for key in sub_dict if len(sub_dict[key]) < 2]
    for this_key in remove_keys:
        sub_dict.pop(this_key)
    return sub_dict


def dict_values_to_list(source_dict: dict) -> List[List[str]]:
    return [source_dict[key] for key in source_dict if len(source_dict[key]) > 1]


def clean_stat_dict(files_dict: dict) -> dict:
    # clean up the data before returning
    files_dict['size'] = clear_single_entries(files_dict['size'])
    files_dict['hardlinks'] = dict_values_to_list(files_dict['hardlinks'])
    return files_dict


# noinspection SpellCheckingInspection
def hash_this_file(file_list: List) -> dict:
    read_this_file = ''
    file_hashes_dict = {}
    for this_file in file_list:
        # noinspection PyBroadException
        try:
            read_this_file = open(this_file, 'rb')
        except:
            read_this_file.close()
            continue
        else:
            hasher = hashlib.new(hash_algo)
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
    # If you want single-thread
    # for this_file in file_size_dict.values():
    #    file_hashes_dict.update(hash_this_file(this_file))
    mypool = Pool(processes=parallel)
    list_of_dicts = mypool.map(hash_this_file, file_size_dict.values())
    mypool.close()
    for this_dict in list_of_dicts:
        file_hashes_dict.update(this_dict)
    return file_hashes_dict


def get_duplicate_files(sub_dict: dict) -> List[List[str]]:
    sub_dict = get_file_hashes(sub_dict)
    return dict_values_to_list(clear_single_entries(sub_dict))


def main(mydir: str) -> dict:
    mydir = os.path.expanduser(mydir)  # gets the absolute path if given in a form like ~/mydir
    if isdir(mydir):
        dup_dict = clean_stat_dict(scan_directory(mydir))
        dup_dict['duplicates'] = get_duplicate_files(dup_dict['size'])
        dup_dict.pop('size')
        # dataprint(dup_dict)
        return dup_dict
    else:
        print('{} is not a directory.'.format(mydir))
        return {'error': '{} is not a directory.'.format(mydir)}


main(basedir)
