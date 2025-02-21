#!/bin/bash
set -eu

#
# Registration of atlas onto the autofluorescence channel
# retult: a transformed atlas file to match the autof. channel
#

if [ "$#" -ne 3 ]; then
    echo "run_elastix_data2atlas_PointsTranformix.sh requires 3 input arguments:"
    echo "./run_elastix_data2atlas_PointsTranformix.sh <OUTPUT DIRECTORY> <KIND: plaques or microglia> <AUTOFLUORESCENCE CHANNEL>"
    exit
fi

ELASTIX_PATH=/media/user/SSD1/Athena/SOURCE/elastix-5.2.0-linux
export LD_LIBRARY_PATH=${ELASTIX_PATH}/lib/
elastix="${ELASTIX_PATH}/bin/elastix"
transformix="${ELASTIX_PATH}/bin/transformix"

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

out="$1"
kind="$2"
input_auto="$3"
echo $out
echo $kind
echo $input_auto


# REFERENCE ATLAS
atlas="atlas/ABA_25um_reference_hemisphere_noBulb.nrrd"
ls $atlas

# ANNOTATION ATLAS
atlas_annotation="atlas/selected_atlas_areas_pixel25um_noBulb_2025-02.nrrd"
#atlas_annotation="/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/quantification/output/selected_atlas_areas_pixel25um.nrrd"
ls $atlas_annotation

affine="Lisa/Parameters_affine.txt"
bspline="Lisa/Parameters_Bspline.txt"
ls $affine
ls $bspline
threads=32

outEa=${out}/elastix_affine_LISA_noBulb_preprocessed_Bin2-Cap-Gaus3D2_try20
outEb=${out}/elastix_bspline_LISA_10k_125umGrid1_SmoothAll2_noBulb_BsplineInterpolator_try20
outI=${out}/inverse_transform

outTPC=${out}/transformix_${kind}_Feb2025
mkdir -p "${outEa}"
mkdir -p "${outEb}"
mkdir -p "${outTPC}"
mkdir -p "${outI}"

# registration of atlas onto the autofluorescence channel
if [ ! -f "${outEa}/result.0.nrrd" ]; then
    ${elastix} -out "${outEa}" -m "${input_auto}" -f "${atlas}" -p "${affine}" -threads $threads
fi
if [ ! -f "${outEb}/result.0.nrrd" ]; then
    ${elastix} -out "${outEb}" -m "${input_auto}" -f "${atlas}" -p "${bspline}" -t0 "${outEa}/TransformParameters.0.txt"  -threads $threads
fi

# Estimate inverse transform
if [ ! -f "${outI}/result.0.nrrd" ]; then
    cp "${outEb}/TransformParameters.0.txt" "${outI}"/

    # Modify Bspline parameter file
    cp "${bspline}" "${outI}/parameters_bspline_inv.txt"

    # edit the Bspline file to perform inverse transform
    sed -i "/(Metric/c\(Metric DisplacementMagnitudePenalty)" "${outI}/parameters_bspline_inv.txt"

    # find the inverse transformation
    ${elastix}  -out "${outI}" -m "${atlas}" -f "${atlas}" -p "${outI}/parameters_bspline_inv.txt" -t0 "${outI}/TransformParameters.0.txt"  -threads $threads
fi

# Transformation of a list of points
if [ ! -f "${outTPC}/outputpoints.txt" ]; then
    #points_file=`dirname ${input_auto}`/coordinates_*_${kind}_*.txt
    brainID=`basename ${input_auto} | awk -F  'Brain' '{print $2}' | awk -F  '_' '{printf("%02d\n", $1)}'`
    echo ${brainID}

    points_file="/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/ILASTIK/object_centroids/coordinates_Brain${brainID}_${kind}_centroids.txt"
    ls $points_file

    cp "${outI}/TransformParameters.0.txt" "${outTPC}"/

    # edit the Transform Parameters file
    sed -i "/(InitialTransformParameterFileName/c\(InitialTransformParameterFileName \"NoInitialTransform\" )" "${outTPC}/TransformParameters.0.txt"
    mv "${outTPC}/TransformParameters.0.txt" "${outTPC}/TransformParameters.0ed.txt"

    ${transformix} -def "${points_file}" -out "${outTPC}" -tp "${outTPC}/TransformParameters.0ed.txt" -threads $threads
fi

