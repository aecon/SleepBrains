#!/bin/bash
set -eu

# ilastik folder
i="$HOME/Downloads/ILASTIK_1.3.3/ilastik-1.3.3post3-Linux"  # does not have --distributed version
#i="$HOME/Downloads/ILASTIK-1.4.1b23-Linux"   # does not open
ls $i

# project file
p="/media/user/SSD1/Athena/SOURCE/SleepBrains/ilastik/channel488_Groups1and2_2.ilp"
ls $p

# output directory
odir=`pwd`/out_2025-02-10
mkdir -p ${odir}

# input dataset
# -tif: supported
# -h5:  supported
# -raw: datafile name must be like this: "Z-Y-X-type.raw"
# Loop over input files 
files=`find /media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/Brain* -name "cropped_original_Brain*.h5"`
for f in ${files[@]}; do
    echo "Processing:" $f

    # Run ilastik
    (
        cd ${i}
        #mpiexec -n ${Nproc} ./run_ilastik.sh --headless --distributed --readonly=True \
        LAZYFLOW_THREADS=32 ./run_ilastik.sh --headless --readonly=True \
                                --project="${p}" \
                                --output_filename_format="${odir}"/{nickname}_Probabilities.tiff \
                                "${f}"
    )
done

