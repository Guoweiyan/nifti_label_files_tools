# nifti_label_files_tools
This tools bundle is designed to help you process the nifti label files with more efficiency. The label translate and read tool is now aviliable.

## label translate and read tool
### Description
This tool is the script translate_labels.py. Using this tool, you can:
1.(Read mode) Check the information of label files in the specific folder, including the labels containing in the label files, voxels/pixels count per label and corresponding percentage to the whole label image. Meanwhile it can find if there exists label files that do not contain all of the labels in the folder and find the missing labels. F.e., in BraTS2020 training dataset, we have 369 training cases with corresponding segmentation (label) files, while label 0, 1, 2, 4 represents different type of tissues/lesions. The dice loss that usually used for this dataset (as well as other medical dataset) will be unstable if there are few voxels for some labels in some cases, and there also exist a phenomenon that some labels even do not appear in some special cases . To get more information about this kind of dataset, you can try this tool in "read" mode.
2.(Translate mode) Translate (replace) some specific labels in the label files by your customed ones. F.e., we have the label files containing labels 0, 1, 2, 4 in BraTS2020 dataset, but we need the labels to be continious sometimes, you can use this tool to translate label 4 -> label 3 to get your work easy. Or when we use the merged dice loss in model testing, which may compute the joint dice for (label 1 + label 2) , or (label 1 + label 3), this tool can also be helpful.

### Usage
usage: translate_labels.py [-h] [--output_folder OUTPUT_FOLDER]
                           [--original_labels ORIGINAL_LABELS]
                           [--newer_labels NEWER_LABELS] [--reg REG]
                           mode input_folder

positional arguments:
  mode                  Mode, can be 'read' or 'translate'
  input_folder          The input folder containing label files

optional arguments:
  -h, --help            show this help message and exit
  --output_folder OUTPUT_FOLDER
                        The output folder where the new label files will be
                        stored
  --original_labels ORIGINAL_LABELS
                        The original labels list, f.e. [0, 1, 2, 3]
  --newer_labels NEWER_LABELS
                        The newer labels list corresponding to original, f.e.
                        [0, 1, 1, 5] means to translate all aforementioned
                        label 2 to label 1 and label 3 to label 5
  --reg REG             Custom your label filename regex to catch the ID, it
                        can simplify the output in most of the time
                        

### More Information
About the original_labels and newer_labels parameters: these two parameters can be strings like this "[1, 2, 3]", representing a list splited by ",", and the bracket is not nessesary.
The original_labels indicates the labels to be replaced (translated), and the newer_labels indicates the corresponding labels to replace (translate). For each label in the original_labels, it will be replaced by the label of the same index of the newer_labels. So, the two parameters must have the same length!
F.e., original_labels = [2, 3, 5] with newer_labels = [1, 2, 3] means to translate label 2 -> label 1, label 3 -> label 2 and label 5 -> label 3; original_labels = [1, 2, 3] with newer_labels = [1, 1, 2] means to merge labels 1 and label 2 to label 1, and translate label 3 to label 2 (The first element of the two parameters [1] and [1] is just for example and not nessesary, because it means a label 1 -> label 1 translation which does nothing, you can simply remove it).

Finally, Hope my tools can help you with your works.
