#! /usr/bin/env python
import os
import shutil
import re
import numpy as np
from argparse import ArgumentParser


def args_check(args):
    assert os.path.isdir(args.from_folder), "The from_folder must exist! "
    if not os.path.isdir(args.to_folder):
        os.mkdir(args.to_folder)
    args.n = int(args.n)
    assert args.n > 0, "n must greater than zero! "

    return args


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("from_folder", help="Your folder containing all of data where you want to choose from")
    arg_parser.add_argument("to_folder", help="Copy the chosen data to here")
    arg_parser.add_argument("n", help="Choose how many items")
    arg_parser.add_argument("reg", help="The regex to find your items in the folder")
    arg_parser.add_argument("--ignore_reg", help="The regex to match the item you don't want to choose")

    args = arg_parser.parse_args()
    args = args_check(args)

    reg = re.compile(args.reg)
    file_list = [file for file in os.listdir(args.from_folder) if reg.search(file)]
    if args.ignore_reg:
        except_reg = re.compile(args.except_reg)
        file_list = [file for file in file_list if not except_reg.search(file)]
    print(f"There are {len(file_list)} items found in the from_folder")
    rng = np.random.default_rng()
    chosen_file_list = list(rng.choice(file_list, size=args.n, replace=False))

    for item in chosen_file_list:
        ab_path = os.path.join(args.from_folder, item)
        if os.path.isdir(ab_path):
            shutil.copytree(ab_path, os.path.join(args.to_folder, item))
        elif os.path.isfile(ab_path):
            shutil.copy(ab_path, os.path.join(args.to_folder, item))
        else:
            print(f"Warning, the file or folder {ab_path} not existing")

    print(f"finished copying {args.n} items")
    return


if __name__ == "__main__":
    main()