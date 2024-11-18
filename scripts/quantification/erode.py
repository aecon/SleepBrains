import os
import sys
import nrrd
import argparse
import skimage.io
import numpy as np
from pathlib import Path
from allensdk.core.reference_space_cache import ReferenceSpaceCache

import img3


def erode_mask(mask, tmp_dir):
    """
    Return atlas mask with pixel values:
    * 1: excluded regions inside and outside the atlas
    * 0: everywhere else
    """

    # Parameters
    erosion_steps = 2
    fatlasD = "/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/4_alignment/atlas/ABA_25um_distance_to_surface_halfbrain.nrrd"

    # Temporary work arrays
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    keep    = img3.mmap_create("%s/keep.raw" % tmp_dir, np.dtype("uint8"), mask.shape)
    tmp     = img3.mmap_create("%s/tmp.raw"  % tmp_dir, np.dtype("uint8"), mask.shape)

    # Binarize exclusion mask
    mask[mask>0] = 1

    # Exclude area outside atlas
    atlasD, _ = nrrd.read(fatlasD)
    mask[atlasD==0] = 1

    # Erode
    fliped_mask = np.ones(np.shape(mask))
    fliped_mask[mask==1] = 0

    tmp[:,:,:] = fliped_mask[:,:,:]
    keep[:,:,:] = 0
    img3.erosion(tmp, erosion_steps, keep)

    eroded_mask = np.zeros(np.shape(mask))
    eroded_mask[keep==0] = 1

    return eroded_mask

