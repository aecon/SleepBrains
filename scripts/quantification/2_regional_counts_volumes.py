import os
import nrrd
import numba
import argparse
import skimage.io
import numpy as np

from generate_atlas_masks import brain_regions_include


# DESIGNED TO RUN WITH PARALLEL=FALSE.
@numba.jit(nopython=True, parallel=False, fastmath=True)
def count_points_in_region(regions, indices, Nregions):
    nx,ny,nz = regions.shape
    Np = len(indices)
    counts_per_region = np.zeros(Nregions, dtype=np.int64)
    for pi in range(Np):
        i = indices[pi,0]
        j = indices[pi,1]
        k = indices[pi,2]
        if ((i<nx) and (j<ny) and (k<nz)):  # exclude points outside Atlas space
            region_id = regions[i,j,k]
            if region_id > 0:  # if not background
                counts_per_region[region_id-1] += 1
    return counts_per_region



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

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, nargs='+', required=True, help="txt, list of aligned points")
    parser.add_argument('-o', type=str, required=True, help="centroid or allvoxels")
    args = parser.parse_args()

    file_atlas = '/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/alignment/atlas/selected_atlas_areas_pixel25um_noBulb.nrrd'
    pixel_size = 25  # microns per pixel

    # Load atlas
    regions, _ = nrrd.read(file_atlas)
    regions = regions.astype(np.int64)
    Nregions = len(np.unique(regions))-1  # subtract 1 for background
    assert(len(brain_regions_include)==Nregions)

    for file_points in args.i:
        print("Processing:", file_points)
    
        # Load transformed points
        points = load_points(file_points)
        indices = (points // pixel_size).astype(np.int64)

        # Get number of points per region
        counts_per_region = count_points_in_region(regions, indices, Nregions)

        # Export to file
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(file_points)))
        output_file = basedir + os.sep + "region_counts_" + os.path.basename(basedir).split("_")[0] + "_%s.txt" % args.o
        print(output_file)
        with open(output_file, "w") as f:
            for i in range(Nregions):
                f.write("%s %d\n" % (brain_regions_include[i], counts_per_region[i]))

