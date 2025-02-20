import os
import sys
import glob
import nrrd
import numba
import skimage.io
import numpy as np
import pandas as pd
from generate_atlas_masks import brain_regions_include


# DESIGNED TO RUN WITH PARALLEL=FALSE.
@numba.jit(nopython=True, parallel=False, fastmath=True)
def count_points_in_region(regions, indices, volumes, avgprob, Nregions):
    nx,ny,nz = regions.shape
    Np = len(indices)
    counts_per_region = np.zeros(Nregions, dtype=np.int64)
    volumes_per_region = np.zeros(Nregions, dtype=np.int64)
    total_prob_per_region = np.zeros(Nregions, dtype=np.float32)
    for pi in range(Np):
        i = indices[pi,0]
        j = indices[pi,1]
        k = indices[pi,2]
        if ((i<nx) and (j<ny) and (k<nz)):  # exclude points outside Atlas space
            region_id = regions[i,j,k]
            if region_id > 0:  # if not background
                counts_per_region[region_id-1] += 1
                volumes_per_region[region_id-1] += volumes[pi]
                total_prob_per_region[region_id-1] += avgprob[pi]
    region_volumes = np.zeros(Nregions)
    for i in range(Nregions):
        region_volumes[i] = np.sum(regions==i+1)

    return counts_per_region, volumes_per_region, total_prob_per_region, region_volumes



def load_points(file_points):
    database = np.genfromtxt(file_points, dtype='str', delimiter=";")
    Np = len(database)
    points = np.zeros((Np,3), dtype=np.float32)
    for i in range(Np):
        s = database[i,4].split("[")[1].split("]")[0]
        p = np.fromstring(s, dtype=float, sep=" ")
        assert(len(p)==3)
        points[i,0] = p[0]
        points[i,1] = p[1]
        points[i,2] = p[2]
    return points



if __name__ == "__main__":

    channel = "488"
    paths_centroids = sorted(glob.glob("/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain*_stitched/align/transformix_%s_Feb2025/outputpoints.txt" % channel))

    file_atlas = '/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/selected_atlas_areas_pixel25um_noBulb_2025-02.nrrd'
    pixel_size = 25  # microns per pixel

    # Load atlas
    regions, _ = nrrd.read(file_atlas)
    regions = regions.astype(np.int64)
    Nregions = len(np.unique(regions))-1  # subtract 1 for background
    assert(len(brain_regions_include)==Nregions)

    for file_centroids in paths_centroids:
        print("Processing:")
        print(file_centroids)
        brainID = int(os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(file_centroids)))).split("Brain")[1].split("_")[0])
        file_measurements = "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/ILASTIK/predictions_488_allBrains_ilp-v4/nrrd/coordinates_Brain%02d_488_centroids_with_measurements.csv" % brainID
        print(file_measurements)


        kind = "centroids"
        file_points =  file_centroids

        # Load transformed points
        points = load_points(file_points)
        Npoints = len(points)
        indices = (points // pixel_size).astype(np.int64)

        # Load file with per-object measurements
        df = pd.read_csv(file_measurements)
        volumes = df["NumberOfVoxels"].to_numpy()  # In Voxels
        avgprob = df[" AverageProbability"].to_numpy()

        # Get number of points, volumes and associated probabilities
        counts_per_region, volumes_per_region, total_prob_per_region, region_volumes = count_points_in_region(regions, indices, volumes, avgprob, Nregions)

        # Export to file
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(file_points)))
        brainid = os.path.basename(basedir).split("_")[0]
        output_file = basedir + os.sep + "Brain%02d_region_counts_volumes_probabilities_%s" % (brainID, channel) + brainid + "_%s.txt" % kind
        print(output_file)
        with open(output_file, "w") as f:
            f.write("%s %s %s %s\n" % ("Region", "ObjCounts" "ObjVolumes" "ObjProbability" "RegionVolume") )
            for i in range(Nregions):
                f.write("%s %d\n" % (brain_regions_include[i], counts_per_region[i], volumes_per_region[i], total_prob_per_region[i], region_volumes[i]))

