#! /usr/bin/env python
import os
import re
import shutil
from argparse import ArgumentParser

# this tool is to convert the BraTS cases to the specific organization pattern for nnU-Net

def main():
    args_parser = ArgumentParser()
    args_parser.add_argument("original_folder")
    args_parser.add_argument("to_folder")

    args = args_parser.parse_args()
    label_folder = os.path.join(args.to_folder, "labels")
    if not os.path.isdir(args.to_folder):
        os.mkdir(args.to_folder)
    if not os.path.isdir(label_folder):
        os.mkdir(label_folder)

    reg = re.compile("Training")
    subfolder_list = [i for i in os.listdir(args.original_folder) if reg.search(i) and os.path.isdir(os.path.join(args.original_folder, i))]
    postfix = ["_0000.nii.gz", "_0001.nii.gz", "_0002.nii.gz", "_0003.nii.gz"]
    label_postfix = ".nii.gz"
    original_postfix = ["_t1.nii.gz", "_t1ce.nii.gz", "_t2.nii.gz", "_flair.nii.gz"]
    ori_label_postfix = "_seg.nii.gz"
    print(f"Totally {len(subfolder_list)} cases")
    for folder in subfolder_list:
        path = os.path.join(args.original_folder, folder)
        for i in range(4):
            assert os.path.isfile(os.path.join(path, folder+original_postfix[i]))
            shutil.copy(os.path.join(path, folder+original_postfix[i]), os.path.join(args.to_folder, folder+postfix[i]))
        assert os.path.isfile(os.path.join(path, folder+ori_label_postfix))
        shutil.copy(os.path.join(path, folder+ori_label_postfix), os.path.join(label_folder, folder+label_postfix))
        print(f"{folder} processed")


if __name__ == "__main__":
    main()