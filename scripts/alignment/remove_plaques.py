import os
import sys
import nrrd
import numba
import argparse
import numpy as np
import pandas as pd
import skimage.io


@numba.jit(nopython=True, parallel=True, fastmath=True)
def remove_plaques(raw, labeled_brain, output):
    nx,ny,nz = raw.shape  # checked: nrrd load data in (Y,X,Z) format
    halfdist = 30.
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):

                label = labeled_brain[i,j,k]
                if label > 1:
                    x0 = int(np.maximum(0.,  i-halfdist))
                    x1 = int(np.minimum(nx,  i+halfdist))
                    y0 = int(np.maximum(0.,  j-halfdist))
                    y1 = int(np.minimum(ny,  j+halfdist))

                    t = 0.
                    total = 0.
                    for ii in range(x0,x1):
                        for jj in range(y0,y1):
                            if labeled_brain[ii,jj,k] == 0:
                                total += raw[ii,jj,k]
                                t += 1
                    if t>0:
                        value = total / t
                        output[i,j,k] = np.floor(value)



parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, nargs='+', required=True, help="nrrd, raw 488")
args = parser.parse_args()

for file_raw in args.i:
    print("Processing:", file_raw)

    # Set paths
    file_labels = os.path.dirname(file_raw) + os.sep + "labelled_segmented_"  + os.path.basename(file_raw).split(".tif")[0] + ".nrrd"
    
    # Check if files exist
    if not os.path.exists(file_labels):
        print("File not found... Exiting.", file_labels)
        sys.exit()
    
    # Load data
    print("Loading raw data ...", file_raw)
    raw, _ = nrrd.read(file_raw)
    raw = np.asarray(raw, dtype=np.uint16)
    print("Loading labeled data ...", file_labels)
    labeled_brain, _ = nrrd.read(file_labels)
    labeled_brain = np.asarray(labeled_brain, dtype=np.float64)
    
    print("Removing plaques ...")
    edited_brain = np.zeros(np.shape(raw), dtype=np.uint16)
    edited_brain[:,:,:] = raw[:,:,:]
    remove_plaques(raw, labeled_brain, edited_brain)
    
    # Save edited brain
    print("Writing edited brain ...")
    outputfile = '%s_forAlignment.tif' % file_raw
    skimage.io.imsave(outputfile, edited_brain.T, plugin="tifffile", check_contrast=False)

