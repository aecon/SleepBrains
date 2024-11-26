import os
import sys
import argparse
import numpy as np
import pandas as pd


# DESIGNED TO RUN WITH PARALLEL=FALSE.
@numba.jit(nopython=True, parallel=False, fastmath=True)
def remove_plaques(raw, volumes, coordinates, counts_cumsum, intensity_mean, intensity_std):
#                     uint16  int64    .   int64      int64         float32        float32
    nx,ny,nz = raw.shape  # checked: nrrd loads data in (Y,X,Z) format
    Nlabels = len(volumes)
    Nc = len(coordinates)

    # Loop over the objects
    for idx in range(1, Nlabels):  # ignore the first object
        base = counts_cumsum[idx-1] * 3
        volume = volumes[idx]
        intensities = np.zeros(volume, dtype=raw.dtype)
        # Loop over the pixel of the particular object
        for i in range(volume):
            g = int(base + i*3)
            assert((g+2) < Nc)
            pi = coordinates[g + 0]
            pj = coordinates[g + 1]
            pk = coordinates[g + 2]
            assert((pi<nx) and (pj<ny) and (pk<nz))
            intensities[i] = raw[pi,pj,pk]

        # At the end of the loop for this object, compute mean, std
        intensity_mean[idx] = np.nanmean(intensities.astype(np.float32))
        intensity_std[idx]  = np.nanstd( intensities.astype(np.float32))


# DESIGNED TO RUN WITH PARALLEL=FALSE. PARALLEL VERSION WILL HAVE RACE CONDITION ON COUNTER.
@numba.jit(nopython=True, parallel=False, fastmath=True)
def _get_coordinates(labels3, volumes, counts_cumsum, coordinates):
    nx,ny,nz = labels3.shape  # checked: nrrd loads data in (Y,X,Z) format
    counter = np.zeros(len(volumes), dtype=np.int64)
    Nc = len(coordinates)

    # Loop over the image, once
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):  # C order (row major)
                label = labels3[i,j,k]
                if label > 1:  # ignore the first object
                    idx = label-1
                    base = counts_cumsum[idx-1] * 3
                    g = base + counter[idx] * 3
                    assert(g < Nc)
                    coordinates[g + 0] = i
                    coordinates[g + 1] = j
                    coordinates[g + 2] = k
                    counter[idx] = counter[idx] + 1
    for i in range(1,len(volumes)):
        assert(counter[i] == volumes[i])


def find_file(path):
    if os.path.exists(path):
        print("Found file:", path)
    else:
        print("File not found:", path)
        sys.exit()
    return path


def load_nrrd(path, dtype):
    print("Loading:", os.path.basename(path))
    data, _ = nrrd.read(path)
    data = np.asarray(data, dtype=dtype)
    return data


def get_coordinates(labels3, volumes):
        print("Computing intensity stats ...")
        sumVolumes = np.sum(volumes)
        print("Sum of all object volumes:", sumVolumes)
        assert(sumVolumes.dtype == np.int64)
        coordinates = np.zeros((sumVolumes*3), dtype=np.int64)
        counts_cumsum  = np.cumsum(volumes)
        assert(counts_cumsum.dtype == np.int64)
        print("- Getting coordinates")
        _get_coordinates(labels3, volumes, counts_cumsum, coordinates)
        return counts_cumsum, coordinates




if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, nargs='+', help="csv, list with object measurements")
    args = parser.parse_args()

    # Find paths
    for file_csv in args.i:
        print("\nProcessing:", file_csv)

        file_labels = find_file( os.path.dirname(file_csv) + os.sep + "labelled_" + os.path.basename(file_csv).split("-morpho")[0] + ".nrrd" )

        # Load csv data
        # - Label,VoxelCount,Volume,SurfaceArea,Sphericity,Centroid.X,Centroid.Y,Centroid.Z,InscrBall.Center.X,InscrBall.Center.Y,InscrBall.Center.Z,InscrBall.Radius,IntensityAvg,IntensityStd
        print("Loading csv ...")
        data = pd.read_csv(file_csv)
        labels  = data["Label"].to_numpy()
        volumes = data["VoxelCount"].to_numpy()
        cx      = data["Centroid.X"].to_numpy()
        cy      = data["Centroid.Y"].to_numpy()
        cz      = data["Centroid.Z"].to_numpy()
        spericity=data["Sphericity"].to_numpy()
        IntensityAvg=data["IntensityAvg"].to_numpy()
        IntensityStd=data["IntensityStd"].to_numpy()
        
        eps = np.finfo(np.float32).eps
        IntensityRatio = IntensityStd / (IntensityAvg + eps) * 100.

        # Checks
        assert(len(labels) == np.max(labels))
        assert(volumes.dtype == np.int64)
        assert(labels.dtype == np.int64)

        # Filter-out non-plaque objects
        ts = 0.2    # >
        tv = 40000  # <
        ti = 15     # >
        idx = (spericity>ts) * (volumes<tv) * (IntensityRatio>ti)

        lbl_plaque = labels[idx]
        v_plaque = volumes[idx]
        cx_plaque = cx[idx]
        cy_plaque = cy[idx]
        cz_plaque = cz[idx]

        # Generate new plaques dataframe
        df_plaque = pd.DataFrame(columns=['Label', 'VoxelCount', 'Centroid.X', 'Centroid.Y', 'Centroid.Z'])
        df_plaque['Label'] = lbl_plaque
        df_plaque['VoxelCount'] = v_plaque
        df_plaque['Centroid.X'] = cx_plaque
        df_plaque['Centroid.Y'] = cy_plaque
        df_plaque['Centroid.Z'] = cz_plaque

        # Export to csv
        print("Exporting to csv ...")
        output_path = file_csv + "_PLAQUES.csv"
        df_plaque.to_csv(output_path, index=False)



        # Load 3D data
        print("Reading 3D labels")
        labels3F = load_nrrd(file_labels, dtype=np.float32)  # MLJ output is in float32
        labels3  = labels3F.astype(np.int64)
        assert(np.max(labels) == np.max(labels3))
        assert(labels3.dtype == np.int64)

        # --> Step 1: Get all coordinates per object
        counts_cumsum, coordinates = get_coordinates(labels3, volumes)

        # Save coordinates of true plaques
        sumVolumesPlaques = np.sum(v_plaque)
        assert(sumVolumesPlaques.dtype == np.int64)
        coordinates_plaques = np.zeros((sumVolumesPlaques*3), dtype=np.int64)
        counts_cumsum_plaques  = np.cumsum(v_plaque)
        assert(counts_cumsum_plaques.dtype == np.int64)




        # --> Step 2: Exclude non-plaques from candidate objects
        labels3_plaques = np.zeros(labels3.shape, dtype=labels3.dtype)
        print("- Excluding non-plaques")
        remove_plaques(lbl_plaque, coordinates, counts_cumsum, labels3_plaques)

        # Save to tif file
        print("Saving brain with true plaques ...")
        skimage.io.imsave('%s_colouredIntensityRatio.tif' % file_labels, brain_coloured_int.T, plugin="tifffile", check_contrast=False)


        del labels3
        del coordinates
        del labels
        del volumes
        del counts_cumsum

