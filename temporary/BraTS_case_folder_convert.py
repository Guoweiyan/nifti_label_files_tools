#! /usr/bin/env python
import os
import re
import shutil
from argparse import ArgumentParser



def main():
    args_parser = ArgumentParser()
    args_parser.add_argument("original_folder")
    args_parser.add_argument("to_folder")

    args = args_parser.parse_args()
    if not os.path.isdir(args.to_folder):
        os.mkdir(args.to_folder)
    reg = re.compile("Training")
    subfolder_list = [i for i in os.listdir(args.original_folder) if reg.search(i) and os.path.isdir(i)]
    postfix = ["_0000.nii.gz", "_0002.nii.gz", "_0003.nii.gz", "_0004.nii.gz"]
    original_postfix = ["_t1.nii.gz", "_t1ce.nii.gz", "_t2.nii.gz", "_flair.nii.gz"]
    print(f"Totally {len(subfolder_list)} cases")
    for folder in subfolder_list:
        path = os.path.join(args.original_folder, folder)
        for i in range(4):
            assert os.path.isfile(os.path.join(path, folder+original_postfix[i]))
            shutil.copy(os.path.join(path+original_postfix[i]), os.path.join(args.to_folder, folder+postfix[i]))
        print(f"{folder} processed")


if __name__ == "__main__":
    main()