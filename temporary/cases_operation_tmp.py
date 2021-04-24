#! /usr/bin/env python
import os
import shutil
import re
from argparse import ArgumentParser

# this tool is thought to be useful when you choose some cases from your whole dataset and copy them to the desired
# training folder but forget to process other cases to the test folder.


def main():
    args_parser = ArgumentParser()
    args_parser.add_argument("whole_dataset")
    args_parser.add_argument("selected_folder")
    args_parser.add_argument("others_to")
    args = args_parser.parse_args()

    if not os.path.isdir(args.others_to):
        os.mkdir(args.others_to)

    reg = re.compile("Training")
    whole_file_list = [file for file in os.listdir(args.whole_dataset) if reg.search(file)]
    selected_file = [file for file in os.listdir(args.selected_folder) if reg.search(file)]

    file_list_to_copy = [file for file in whole_file_list if file not in selected_file]

    print("Copying")
    for file in file_list_to_copy:
        original_path = os.path.join(args.whole_dataset, file)
        to_path = os.path.join(args.others_to, file)
        if os.path.isdir(original_path):
            shutil.copytree(original_path, to_path)
        else:
            shutil.copy(original_path, to_path)

    print("Finished")


if __name__ == "__main__":
    main()