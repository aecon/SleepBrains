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

affine="elastix/affine.txt"
bspline="elastix/bspline_data2atlas.txt"
ls $affine
ls $bspline
threads=32

#outEa=${out}/elastix_affine_noBulb_try12_Bin2_Gaus3D-1
#outEa=${out}/elastix_affine_noBulb_try11 #_Bin2_Gaus3D-1
outEa=${out}/elastix_affine_noBulb_preprocessed_Bin2-Cap-Gaus3D2_try20 #_

outEb=${out}/elastix_bspline_10k_125umGrid1_SmoothAll2_noBulb_BsplineInterpolator_try20
#outEb=${out}/elastix_bspline_Grid6-2-1_6ksamples_Smooth4-2-1_withBulb_try05

outT=${out}/transformix
mkdir -p "${outEa}"
mkdir -p "${outEb}"
#mkdir -p "${outT}"

# registration of atlas onto the autofluorescence channel
if [ ! -f "${outEa}/result.0.nrrd" ]; then
    ${elastix} -out "${outEa}" -m "${input_auto}" -f "${atlas}" -p "${affine}" -threads $threads
fi
if [ ! -f "${outEb}/result.0.nrrd" ]; then
    ${elastix} -out "${outEb}" -m "${input_auto}" -f "${atlas}" -p "${bspline}" -t0 "${outEa}/TransformParameters.0.txt"  -threads $threads
fi

## transformation of annotation atlas 
#if [ ! -f "${outT}/result.nrrd" ]; then
#    cp "${outEb}/TransformParameters.0.txt" "${outT}"/
#    # edit the Bspline file to use for transforming binary segmented data
#    sed -i "/FinalBSplineInterpolationOrder/c\(FinalBSplineInterpolationOrder 0)" "${outT}"/TransformParameters.0.txt
#    # apply transformation to segmentation
#    ${transformix} -in "${atlas_annotation}" -out "${outT}" -tp "${outT}/TransformParameters.0.txt" -threads $threads
#fi


# TODO:
# Points transformation

