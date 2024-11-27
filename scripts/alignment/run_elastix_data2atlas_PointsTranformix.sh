#!/bin/bash
set -eu

#
# Registration of atlas onto the autofluorescence channel
# retult: a transformed atlas file to match the autof. channel
#

if [ "$#" -ne 2 ]; then
    echo "run_elastix_data2atlas_PointsTranformix.sh requires 2 input arguments:"
    echo "./run_elastix_data2atlas_PointsTranformix.sh <OUTPUT DIRECTORY> <AUTOFLUORESCENCE CHANNEL>"
    exit
fi

ELASTIX_PATH=/media/user/SSD1/Athena/SOURCE/elastix-5.2.0-linux
export LD_LIBRARY_PATH=${ELASTIX_PATH}/lib/
elastix="${ELASTIX_PATH}/bin/elastix"
transformix="${ELASTIX_PATH}/bin/transformix"

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

out="$1"
input_auto="$2"
echo $out
echo $input_auto


# REFERENCE ATLAS
#atlas="atlas/ABA_25um_reference_hemisphere.nrrd"
atlas="atlas/ABA_25um_reference_hemisphere_noBulb.nrrd"
#
# specifically for Brain 9 - missing Cerebellum and Brain stem
#atlas="atlas/ABA_25um_reference_hemisphere_MaskedCerebellumBrainStemVentricles_edited.nrrd"
#
ls $atlas

# ANNOTATION ATLAS
#atlas_annotation="atlas/ABA_25um_annotation_hemisphere.nrrd"
atlas_annotation="/media/user/SSD1/Athena/SOURCE/SleepBrains/scripts/quantification/output/selected_atlas_areas_pixel25um.nrrd"
ls $atlas_annotation

#affine="elastix/affine.txt"
#bspline="elastix/bspline_data2atlas.txt"
affine="Lisa/Parameters_affine.txt"
bspline="Lisa/Parameters_Bspline.txt"
ls $affine
ls $bspline
threads=32

#outEa=${out}/elastix_affine_noBulb_try12_Bin2_Gaus3D-1
#outEa=${out}/elastix_affine_noBulb_try11 #_Bin2_Gaus3D-1
#outEa=${out}/elastix_affine_noBulb_preprocessed_Bin2-Cap-Gaus3D2_try20 #_
outEa=${out}/elastix_affine_LISA_noBulb_preprocessed_Bin2-Cap-Gaus3D2_try20 #_

#outEb=${out}/elastix_bspline_Grid6-2-1_6ksamples_Smooth4-2-1_withBulb_try05
#outEb=${out}/elastix_bspline_10k_125umGrid1_SmoothAll2_noBulb_BsplineInterpolator_try20
outEb=${out}/elastix_bspline_LISA_10k_125umGrid1_SmoothAll2_noBulb_BsplineInterpolator_try20

#outT=${out}/transformix
outTPC=${out}/transformix_centroids
outTPA=${out}/transformix_all
outI=${out}/inverse_transform
mkdir -p "${outEa}"
mkdir -p "${outEb}"
#mkdir -p "${outT}"
mkdir -p "${outTPC}"
mkdir -p "${outTPA}"
mkdir -p "${outI}"

# registration of atlas onto the autofluorescence channel
if [ ! -f "${outEa}/result.0.nrrd" ]; then
    ${elastix} -out "${outEa}" -m "${input_auto}" -f "${atlas}" -p "${affine}" -threads $threads
fi
if [ ! -f "${outEb}/result.0.nrrd" ]; then
    ${elastix} -out "${outEb}" -m "${input_auto}" -f "${atlas}" -p "${bspline}" -t0 "${outEa}/TransformParameters.0.txt"  -threads $threads
fi

# Transformation of annotation atlas 
#if [ ! -f "${outT}/result.nrrd" ]; then
#    cp "${outEb}/TransformParameters.0.txt" "${outT}"/
#
#    ## edit the Bspline file to use for transforming binary segmented data
#    #sed -i "/FinalBSplineInterpolationOrder/c\(FinalBSplineInterpolationOrder 0)" "${outT}"/TransformParameters.0.txt
#
#    # apply transformation to segmentation
#    #${transformix} -in "${atlas_annotation}" -out "${outT}" -tp "${outT}/TransformParameters.0.txt" -threads $threads
#fi


# Estimate inverse transform
if [ ! -f "${outI}/result.nrrd" ]; then
    cp "${outEb}/TransformParameters.0.txt" "${outI}"/

    # edit the Bspline file to perform inverse transform
    sed -i "/(Metric/c\(Metric DisplacementMagnitudePenalty)" "${outI}/TransformParameters.inv.txt"

    exit

    # find the inverse transformation
    ${elastix}  -out "${outI}" -m "${atlas}" -f "${atlas}" -p "${outI}/TransformParameters.inv.txt" -t0 "${outI}/TransformParameters.0.txt"  -threads $threads
fi


exit



# Transformation of a list of points: centroids
if [ ! -f "${outTPC}/outputpoints.txt" ]; then
    points_centroids=`dirname ${input_auto}`/coordinates_plaques_centroids.txt
    ls $points_centroids
    cp "${outEb}/TransformParameters.0.txt" "${outTPC}"/
    ${transformix} -def "${points_centroids}" -out "${outTPC}" -tp "${outTPC}/TransformParameters.0.txt" -threads $threads
fi

# Transformation of a list of points: All plaque voxels
if [ ! -f "${outTPA}/outputpoints.txt" ]; then
    points_allvoxels=`dirname ${input_auto}`/coordinates_plaques_allvoxels.txt
    ls $points_allvoxels
    cp "${outEb}/TransformParameters.0.txt" "${outTPA}"/
    ${transformix} -def "${points_allvoxels}" -out "${outTPA}" -tp "${outTPA}/TransformParameters.0.txt" -threads $threads
fi



