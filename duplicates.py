import os
import argparse
import hashlib
from collections import defaultdict


def get_same_name_files(root_folder):
    name_dict = defaultdict(list)
    tree = os.walk(root_folder)
    for folder_structure in tree:
        folder_path = folder_structure[0]
        files_list = folder_structure[2]
        for file_name in files_list:
            name_dict[file_name].append(
                os.path.join(folder_path, file_name)
            )
    for same_name_files in name_dict.values():
        if len(same_name_files) > 1:
            yield same_name_files


def get_same_size_files(path_list):
    size_dict = defaultdict(list)
    for file_path in path_list:
        size_dict[os.path.getsize(file_path)].append(file_path)
    for same_size_files in size_dict.values():
        if len(same_size_files) > 1:
            yield same_size_files


def get_file_checksum(file_path, block_size=65536):
    sha256_sum = hashlib.sha256()
    with open(file_path, 'rb') as file:
        sha256_sum.update(file.read(block_size))
    return sha256_sum.digest()


def get_same_checksum_files(path_list):
    same_files = []
    checksum_dict = defaultdict(list)
    for file_path in path_list:
        checksum_value = get_file_checksum(file_path)
        checksum_dict[checksum_value].append(file_path)
    for same_checksum_files in checksum_dict.values():
        if len(same_checksum_files) > 1:
            same_files += same_checksum_files
    return same_files


def get_duplicates_path(folder_path, checksum=False):
    duplicates_list = []
    for same_name_files in get_same_name_files(folder_path):
        for same_size_files in get_same_size_files(same_name_files):
            if checksum:
                duplicates_list += get_same_checksum_files(same_size_files)
            else:
                duplicates_list += same_size_files
    return duplicates_list


def parse_arguments():
    argument_parser = argparse.ArgumentParser(
        description='A program which analyze a folder and prints '
                    'duplicates file names if they exist'
    )
    argument_parser.add_argument(
        'folder',
        help='A folder which will be analyzed by the script'
    )
    argument_parser.add_argument(
        '-c',
        '--checksum',
        dest='check_hash_sum',
        action='store_true',
        default=False,
        help='A flag that enables additional checking of files difference '
             'using hash sum'
    )
    return argument_parser.parse_args()


if __name__ == '__main__':
    arguments = parse_arguments()
    folder_path = arguments.folder
    checksum_flag = arguments.check_hash_sum

    duplicates_list = get_duplicates_path(
        folder_path,
        checksum=checksum_flag
    )
    if duplicates_list:
        print('The following files are duplicates:')
    for filename in sorted(duplicates_list):
        print(filename)
