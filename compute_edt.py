#! /usr/bin/env python
import SimpleITK as sitk
import edt
import numpy as np
import os


def main_prog():
    filelist = os.listdir()
    niigzlist = [file for file in filelist if file.endswith(".nii.gz")]
    for niigzfile in niigzlist:
        nparray = sitk.GetArrayFromImage(sitk.ReadImage(niigzfile))
        dt = edt.edt(
            nparray, parallel=1
        )
        sitk.WriteImage(sitk.GetImageFromArray(dt), niigzfile.replace('.nii.gz', '-edt.nii.gz'))


if __name__=="__main__":
    main_prog()