import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def find_file(path):
    if os.path.exists(path):
        print("Found file:", path)
    else:
        print("File not found:", path)
        sys.exit()
    return path


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="csv, list with object measurements, with intensity stats")
args = parser.parse_args()


for file_csv in args.i:
    file_labels = find_file( os.path.dirname(file_csv) + os.sep + os.path.basename(file_csv).split("-morpho")[0] + ".nrrd" )
    
    print("Loading csv ...")
    data = pd.read_csv(file_csv)
    labels  = data["Label"].to_numpy()
    assert(len(labels) == np.max(labels))
    volumes = data["VoxelCount"].to_numpy()
    cx      = data["Centroid.X"].to_numpy()
    cy      = data["Centroid.Y"].to_numpy()
    cz      = data["Centroid.Z"].to_numpy()
    sphericity=data["Sphericity"].to_numpy()
    IntensityAvg=data["IntensityAvg"].to_numpy()
    IntensityStd=data["IntensityStd"].to_numpy()
    
    eps = np.finfo(np.float32).eps
    IntensityRatio = IntensityStd / (IntensityAvg + eps) * 100.
    
    # Thresholds
    THRES_s = 0    # sphericity threshold, should be greater than
    THRES_vmax = 10000  # volume count threshold, should be less than
    THRES_vmin = 2   # volume count threshold, should be more or equal than
    THRES_i = 10     # intensity threholds, should be greater than
    
    
    print("Total object candidates:", len(labels))
    print("Larger than %d voxels:"% THRES_vmax, np.sum(volumes>THRES_vmax))
    print("Smaller than %d voxels:"% THRES_vmin, np.sum(volumes<THRES_vmin))
    print("Lower std/avg probability than %d:"% THRES_i, np.sum(IntensityRatio<THRES_i))
    print("Lower sphericity than %f:"% THRES_s, np.sum(sphericity<THRES_s))
    
    
    # Plots
    plt.figure(figsize=(24, 16))
    
    plt.subplot(2,3,1)
    plt.scatter(sphericity, IntensityRatio, s=2, alpha=0.1, c=IntensityAvg)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('sphericity')
    plt.ylabel('std(p) / avg(p) * 100')
    plt.title('Coloured by Average probability')
    plt.colorbar()
    
    plt.subplot(2,3,2)
    plt.scatter(sphericity, volumes, s=2, alpha=0.1, c=IntensityRatio/100.)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('sphericity')
    plt.ylabel('volume (voxels)')
    plt.title('Coloured by std(p)/avg(p)')
    plt.colorbar()
    
    plt.subplot(2,3,3)
    plt.scatter(volumes, IntensityRatio, s=2, alpha=0.1)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('volume')
    plt.ylabel('std(p) / avg(p) * 100')
    
    # Histograms
    Nbins = 100
    
    plt.subplot(2,3,4)
    plt.hist(sphericity, Nbins, log=True)
    plt.xlabel('sphericity')
    
    plt.subplot(2,3,5)
    plt.hist(IntensityRatio, Nbins, log=True)
    plt.xlabel('IntensityRatio')
    
    plt.subplot(2,3,6)
    plt.hist(volumes, Nbins*2, log=True)
    plt.xlabel('volume')
    
    
    #plt.show()
    output_figure = os.path.dirname(file_csv) + os.sep + os.path.basename(file_csv).split("-morpho")[0] + ".png" 
    plt.savefig(output_figure)
    plt.close()
    
    
    del data, labels, volumes, cx, cy, cz, sphericity, IntensityAvg, IntensityStd, IntensityRatio

