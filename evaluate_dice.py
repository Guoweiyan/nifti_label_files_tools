import SimpleITK as sitk
import numpy as np
import collections
import argparse
import os
import re
import tabulate

from read_translate_labels import read_labels
from read_translate_labels import maybe_get_id_by_name


# This tool is designed to calculate the dice of 2D/3D predicted results.
# Hope to help with your works.


# Merge rule's pattern is defined as follows:
# ((merged labels), (merged labels), ...)
# F.e. ((1, 2), (1, 2, 3), (1, 3)) means to separately calculate three merged dices,
# they are : label 1, 2; label 1, 2, 3; label 1, 3


# process the file list


def evaluate_file_list(pre_file_list_with_path: list, pre_id_list: list, gt_file_list_with_path: list, gt_id_list: list,
                       label_list: list, do_merge=False,
                       merge_rules=None):
    dice_list = []
    for index in range(len(pre_id_list)):
        index_for_gt = gt_id_list.index(pre_id_list[index])
        pre_img = sitk.GetArrayFromImage(sitk.ReadImage(pre_file_list_with_path[index]))
        gt_img = sitk.GetArrayFromImage(sitk.ReadImage(gt_file_list_with_path[index_for_gt]))
        dice = calculate_dice(pre_img, gt_img, do_merge=do_merge,
                              merge_rules=merge_rules, label_list=label_list)
        dice_list.append(dice)

    dice_mean, dice_std = np.mean(dice_list, axis=0), np.std(dice_list, axis=0)
    # print(dice_list)
    # Now, the dice_mean and dice_std is the array with shape n * 1, n is the number of cases
    return dice_mean, dice_std, dice_list


# calculate the dice coefficient for single pair of pre-gt images


def calculate_dice(pre: np.ndarray, gt: np.ndarray, label_list: list, do_merge: bool, merge_rules):
    dice = np.empty([len(label_list), 1])
    for index in range(len(label_list)):
        dice[index] = np.sum(pre[gt == label_list[index]] == label_list[index]) * 2.0 / (
                    np.sum(pre == label_list[index])
                    + np.sum(gt == label_list[index]))
    return dice


def extract_file_list(folder: str, reg):
    file_list = [i for i in os.listdir(folder) if reg.search(i)]
    file_list_with_path = [os.path.join(folder, i) for i in file_list]
    id_list = list(map(int, [reg.search(i).group(1) for i in file_list]))
    return file_list_with_path, file_list, id_list


def args_check(args):
    assert os.path.isdir(args.pre_folder) and os.path.isdir(args.gt_folder), "The input pre_folder and gt_folder must" \
                                                                             " be existing folders! "
    if args.do_merge:
        assert args.merge_rules is not None, "You set the do_merge flag, but no merge rules specified! "
    return


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("pre_folder", help="The folder containing your predicted results")
    argparser.add_argument("gt_folder", help="The folder containing your ground truth annotation files")
    argparser.add_argument("--pre_reg", help="The regex to extract the ids in the pre_folder, and the first catch group"
                                             " of the "
                                             "regex must be the id, you must specify it", default="Training_([\d]+)")
    argparser.add_argument("--gt_reg", help="The regex to extract the ids in the gt_folder, and the first catch group"
                                            " of the "
                                            "regex must be the id, you must specify it", default="Training_([\d]+)")
    argparser.add_argument("--do_merge", action="store_true", help="Whether to do merged dice calculation, False by "
                                                                   "default.")
    argparser.add_argument("--merge_rules", help="Custom your rules for calculating merged dice coefficient")
    args = argparser.parse_args()
    args_check(args)
    gt_reg = re.compile(args.gt_reg)
    pre_reg = re.compile(args.pre_reg)

    pre_file_list_with_path, pre_file_list, pre_id_list = extract_file_list(args.pre_folder, pre_reg)
    gt_file_list_with_path, gt_file_list, gt_id_list = extract_file_list(args.gt_folder, gt_reg)
    assert len(set(pre_id_list)) == len(pre_id_list) and len(set(gt_id_list)) == len(gt_id_list), "There existing the" \
                                                                                                  " same ids in you " \
                                                                                                  "folder!"
    assert set(pre_id_list) <= set(gt_id_list), "The ground truth folder do not contain all the ids in the " \
                                                "prediction folder!"
    print(f"There's totally {len(pre_id_list)} prediction results and {len(gt_id_list)} ground truth annotations")

    #
    pre_labels_set, _, _ = read_labels(pre_file_list_with_path, args.pre_folder, args.pre_reg)
    gt_labels_set, _, _ = read_labels(gt_file_list_with_path, args.gt_folder, args.gt_reg)
    assert pre_labels_set == gt_labels_set, "The labels in the prediction folder do not match labels in the ground " \
                                            "truth folder"
    labels_list = list(pre_labels_set)
    print(labels_list)

    # Todo: Call the calculate function
    dice_mean, dice_std, dice_list = evaluate_file_list(pre_file_list_with_path, pre_id_list, gt_file_list_with_path,
                                                        gt_id_list, labels_list)
    print("The dice mean is :")
    print(dice_mean)


if __name__ == "__main__":
    main()
