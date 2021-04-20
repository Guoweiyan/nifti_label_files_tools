import SimpleITK as sitk
import numpy as np
import collections
import argparse
import os
import re
from tabulate import tabulate

from read_translate_labels import read_labels
from read_translate_labels import maybe_get_id_by_name

# This tool is designed to calculate the dice of 2D/3D predicted results.
# Hope to help with your works.


# Merge rule's pattern is defined as follows:
# ((merged labels) -> output label, (merged labels) -> output label, ...)
# F.e. ((1, 2) -> 1; (1, 2, 3) -> 2; (3) ->3) means to separately calculate three merged dices,
# they are : label 1, 2; label 1, 2, 3; label 3, and the corresponding output labels are 1, 2, 3
MERGE_REG_STR = "\(([\d\,]+)\)->([\d]+)"  # use this regex to match the merge rules


# process the file list


def evaluate_file_list(pre_file_list_with_path: list, pre_id_list: list, gt_file_list_with_path: list, gt_id_list: list,
                       label_list: list, do_merge=False,
                       merge_rules_str=None):
    dice_list = []
    if not do_merge:
        for index in range(len(pre_id_list)):
            index_for_gt = gt_id_list.index(pre_id_list[index])
            pre_img = sitk.GetArrayFromImage(sitk.ReadImage(pre_file_list_with_path[index]))
            gt_img = sitk.GetArrayFromImage(sitk.ReadImage(gt_file_list_with_path[index_for_gt]))
            dice = calculate_dice(pre_img, gt_img, do_merge=False,
                                  label_list=label_list)
            dice_list.append(dice.flatten().tolist())
        dice_mean, dice_std = np.mean(dice_list, axis=0).flatten().tolist(), np.std(dice_list, axis=0).flatten().tolist()
        # print(dice_list)
        # Now, the dice_mean and dice_std is the array with shape n * 1, n is the number of cases
        return dice_mean, dice_std, dice_list, label_list
    else:
        rules_reg = re.compile(MERGE_REG_STR)
        merge_rules_str = merge_rules_str.replace(" ", "").split(";")
        rules = []
        for rule_str in merge_rules_str:
            [merged_labels_str, new_label_str] = rules_reg.search(rule_str).groups("1,2")
            merged_labels = list(map(int, merged_labels_str.split(",")))
            new_label = int(new_label_str)
            rules.append([merged_labels, new_label])
        assert len(rules) > 0, "You set the do_merge flag but I can't recognize any merge rules in your input"
        for index in range(len(pre_id_list)):
            index_for_gt = gt_id_list.index(pre_id_list[index])
            pre_img = sitk.GetArrayFromImage(sitk.ReadImage(pre_file_list_with_path[index]))
            gt_img = sitk.GetArrayFromImage(sitk.ReadImage(gt_file_list_with_path[index_for_gt]))
            dice = calculate_dice(pre_img, gt_img, label_list, do_merge=True, merge_rules=rules)
            dice_list.append(dice.flatten().tolist())
        dice_mean, dice_std = np.mean(dice_list, axis=0).flatten().tolist(), np.std(dice_list, axis=0).flatten().tolist()
        new_label_list = [new_label for [_, new_label] in rules]
        return dice_mean, dice_std, dice_list, new_label_list


# calculate the dice coefficient for single pair of pre-gt images
# Note: this function will return an numpy.ndarray, not a list. You may need to flatten it and make list from it

def calculate_dice(pre: np.ndarray, gt: np.ndarray, label_list: list, do_merge: bool, merge_rules=None):
    if not do_merge:
        dice = np.empty([len(label_list), 1])
        for index in range(len(label_list)):
            # In the case of some labels not existing in this case
            if not (gt == label_list[index]).any():
                if (pre == label_list[index]).any():
                    dice[index] = 0
                else:
                    dice[index] = 1
            else:
                dice[index] = np.sum(pre[gt == label_list[index]] == label_list[index]) * 2.0 / (
                        np.sum(pre == label_list[index])
                        + np.sum(gt == label_list[index]))
        return dice
    else:
        assert merge_rules is not None
        dice = np.empty([len(merge_rules), 1])
        for index in range(len(merge_rules)):
            [merged_label_list, new_label] = merge_rules[index]
            pre_tmp = np.zeros(pre.shape)
            gt_tmp = np.zeros(gt.shape)
            for label in merged_label_list:
                pre_tmp[pre == label] = new_label
                gt_tmp[gt == label] = new_label
            dice[index] = calculate_dice(pre_tmp, gt_tmp, [new_label, ], do_merge=False)
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
    argparser.add_argument("--merge_rules", help="Custom your rules for calculating merged dice coefficient, "
                                                 "Merge rule's pattern is defined as follows: "
                                                 "((merged labels) -> output label, "
                                                 "(merged labels) -> output label, ...)"
                                                 "F.e. ((1, 2) -> 1; (1, 2, 3) -> 2; (3) ->3) means to separately "
                                                 "calculate three merged dices,"
                                                 "they are : label 1, 2; label 1, 2, 3; label 3, and the corresponding "
                                                 "output labels are 1, 2, 3")
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
    print("Checking labels in the pre and gt folders:")
    pre_labels_set, _, _ = read_labels(pre_file_list_with_path, args.pre_folder, args.pre_reg)
    gt_labels_set, _, _ = read_labels(gt_file_list_with_path, args.gt_folder, args.gt_reg)
    assert pre_labels_set == gt_labels_set, "The labels in the prediction folder do not match labels in the ground " \
                                            "truth folder"
    labels_list = list(pre_labels_set)
    print(labels_list)

    print("Calculating dice:")
    # Todo: Call the calculate function
    dice_mean, dice_std, dice_list, dice_labels_list = evaluate_file_list(pre_file_list_with_path, pre_id_list,
                                                                          gt_file_list_with_path,
                                                                          gt_id_list, labels_list,
                                                                          do_merge=args.do_merge,
                                                                          merge_rules_str=args.merge_rules)
    table = []
    for index in range(len(pre_id_list)):
        table.append([pre_id_list[index]] + (dice_list[index]))
    table.append(["Mean"] + dice_mean)
    table = tabulate(table, headers=["ID"] + dice_labels_list, tablefmt="grid")
    print(table)
    output_file_name = "dice_info.txt"
    if args.do_merge:
        output_file_name = "merged_dice_info.txt"
    with open(os.path.join(args.pre_folder, output_file_name), "w") as f:
        if args.do_merge:
            print("Merge Rules:", file=f)
            print(args.merge_rules, file=f)
        print("The labels exists in the folder are:", file=f)
        print(labels_list, file=f)
        print(table, file=f)
    # print("The dice mean is :")
    # print(dice_mean)
    # print(dice_list)


if __name__ == "__main__":
    main()
