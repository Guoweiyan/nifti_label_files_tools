# This file is created by Weiyan Guo Ari 2020. Hope to help you with your work
# There can be lots of bugs in it, please feel free to mail me: github@weiyanguo.cn
#

import collections
import numpy as np
import argparse
import SimpleITK as sitk
import os
import re
import pickle
from tabulate import tabulate


def maybe_get_id_by_name(name: str, reg):
    # returns the id if the regex works, otherwise returns the original name string
    if reg.search(name):
        return "ID :" + reg.search(name).group(1)
    else:
        return "filename " + name


def read_label(filelist_with_path:list, input_folder, reg_str):
    # TODO the label-lost checking do not work for the first label file, remain to fix
    labels_set = set()
    labels_info = collections.OrderedDict()
    labels_lost_list = []
    reg = re.compile(reg_str)
    f = open(os.path.join(input_folder, "info.txt"), "w")
    for file in filelist_with_path:
        label_img = sitk.GetArrayFromImage(sitk.ReadImage(file))
        max = label_img.max()
        min = label_img.min()
        possible_classes = list(range(min, max+1))

        existing_classes = []
        num_of_classes_voxels = []
        for c in possible_classes:
            num = np.sum(label_img == c)
            if num == 0:
                continue
            existing_classes.append(c)
            num_of_classes_voxels.append(int(num))
            labels_set.add(c)
        list_item = collections.OrderedDict()
        list_item["filename"] = file
        list_item["existing_labels"] = existing_classes
        list_item["label_voxels_count"] = num_of_classes_voxels
        list_item["label_voxels_ratio"] = [(num_of_classes_voxels[i] / np.sum(num_of_classes_voxels)) for i in range(len(num_of_classes_voxels))]
        list_item["labels_lost"] = [c for c in labels_set if c not in existing_classes]
        labels_info[file] = list_item

        if len(list_item["labels_lost"]):
            labels_lost_list.append(file)
        # print(file)
        # print(list_item)
        table = []
        for item in list_item:
            table.append([item, list_item[item]])
        table = tabulate(table, headers=("Attribute", "Value"), tablefmt="grid")
        print(f"The {maybe_get_id_by_name(file, reg)}'s attributes are listed below:", file=f)
        print(table, file=f)
    # print(labels_set)
    f.close()
    return labels_set, labels_info, labels_lost_list


def translate_labels(filelist: list, input_folder: str, output_folder: str, original_labels: str, newer_labels: str):
    # TODO finish the function
    # extract the translate information from the string
    original_labels, newer_labels = [original_labels.replace("[", ""), newer_labels.replace("[", "")]
    original_labels, newer_labels = [original_labels.replace("]", ""), newer_labels.replace("]", "")]
    ols = original_labels.split(",")
    nls = newer_labels.split(",")
    ol = list(map(np.uint16, ols))
    nl = list(map(np.uint16, nls))

    assert len(ol) == len(nl), "The two labels must be the same size"
    for filename in filelist:
        img = sitk.GetArrayFromImage(sitk.ReadImage(os.path.join(input_folder, filename)))
        oper_nums = len(ol)
        img_translated = np.zeros(img.shape, dtype=np.uint16)
        mask_for_translated = np.zeros(img.shape, dtype=np.uint16)
        for i in range(oper_nums):
            img_translated_tmp = np.where(img == ol[i], np.uint16(nl[i]), np.uint16(0))
            img_translated += img_translated_tmp
            mask_for_translated += img == ol[i]
        img_translated += np.uint16(img) * (mask_for_translated == 0)
        sitk.WriteImage(sitk.GetImageFromArray(img_translated), fileName=os.path.join(output_folder, filename))
        print(f"The {filename} processed")
    return


def args_check(args):
    assert os.path.isdir(args.input_folder) is True
    if args.reg is not None:
        # print(args.reg)
        assert type(args.reg) is str , "The regex must be a string!"
    if args.mode == "translate":
        if args.output_folder is None:
            print("Warning, the output folder is not specified, using default folders named 'translated'"
                  " enclosed by the input folder")
            args.output_folder = os.path.join(args.input_folder, "translated")
        if os.path.isdir(args.output_folder) is not True:
            os.mkdir(args.output_folder)
        # check two input labels' length
        assert args.original_labels is not None and args.newer_labels is not None, "No label list input, please check " \
                                                                                   "your input! "
        assert len(args.original_labels.split(",")) == len(args.newer_labels.split(",")), "The original labels list " \
                                                                                          "do not have the same size " \
                                                                                          "of the newer one, " \
                                                                                          "please check your input! "
    return True


def extract_filelist(args):
    filter_reg = re.compile(".nii.gz")
    filelist = [i for i in os.listdir(args.input_folder) if filter_reg.search(i)]
    if len(filelist) == 0:
        print(f"Error: No label files found in input_folder {args.input_folder}, please check it")
        return None, None
    else:
        print(f"{len(filelist)} label files found")
    filelist_with_path = [os.path.join(args.input_folder, i) for i in filelist]
    return filelist_with_path, filelist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="Mode, can be 'read' or 'translate'")
    parser.add_argument("input_folder", help="The input folder containing label files")
    parser.add_argument("--output_folder", help="The output folder where the new label files will be stored", required=False)
    parser.add_argument("--original_labels", help="The original labels list, f.e. [0, 1, 2, 3]", required=False)
    parser.add_argument("--newer_labels", help="The newer labels list corresponding to original, f.e. [0, 1, 1, 5] "
                                             "means to translate all aforementioned label 2 to label 1 and label 3 to label 5",
                        required=False)
    parser.add_argument("--reg", help="Custom your label filename regex to catch the ID, it can simplify the output "
                                      "in most of the time", default=str("Training_([\d]+)"))

    args = parser.parse_args()
    args_check(args)
    filelist_with_path, filelist = extract_filelist(args)
    assert filelist_with_path is not None and filelist is not None, "There seems no label file in the input folder! "

    if args.mode == "read":
        # read mode
        # To read the label files in the specific folder and analyze some attributes of them.
        # Meanwhile, it can find if there are label files that do not containing all the labels
        labels_set, labels_info, labels_lost_list = read_label(filelist_with_path, args.input_folder, args.reg)
        print(f"The label files contains the following labels:\n {labels_set}")
        if len(labels_lost_list):
            print(f"Please note that {len(labels_lost_list)} files do not have all of the labels, they are:")
            id_reg = re.compile(args.reg)
            table = []
            for l in labels_lost_list:
                # print(f"The {maybe_get_id_by_name(l, id_reg)} lost label {labels_info[l]['labels_lost']}")
                table.append([maybe_get_id_by_name(l, id_reg), labels_info[l]["labels_lost"]])
            table = tabulate(table, headers=("File or ID", "Lost labels"))
            print(table)
            with open(os.path.join(args.input_folder, "label_lost_info.txt"), "w") as f:
                print(table, file=f)
            print("The label lost information is print to the file label_lost_info.txt")
        else:
            print("All label files are of the same labels")
        with open(os.path.join(args.input_folder, "labels_statistic.pkl"), "wb") as f:
            pickle.dump(labels_info, f)
        print(f"The analysis report are written into the txt file in the input folder {args.input_folder}")
        # TODO add more read-friendly output in text format rather than pickle file
    else:
        # Translate mode
        # In this mode, you can translate some labels in the files to other labels by pass a pair of old-new list
        translate_labels(filelist, args.input_folder, args.output_folder, args.original_labels, args.newer_labels)


if __name__ == '__main__':
    main()