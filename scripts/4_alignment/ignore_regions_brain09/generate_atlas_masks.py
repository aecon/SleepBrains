import os
import nrrd
import numpy as np
from regions import generate_region_mask 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONFIGURATION
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Brain regions to exclude
brain_regions_exclude = ['Hindbrain', 'Cerebellum', 'ventricular systems', ]  # 'Midbrain', 'fiber tracts'

# Directory to store quantified results (txt files)
output_dir = "output"

# atlas pixel resolution
resolution = 25


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ATLAS MASKS GENERATION
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    regions_exclude = generate_region_mask(output_dir, "atlas_regions_exclude", brain_regions_exclude, resolution)

    nrrd.write("%s/regions_excluded.nrrd" % output_dir, regions_exclude)

    # Combine into a single mask
    regions_exclude[regions_exclude>0] = 1
    nrrd.write("%s/mask_excuded.nrrd" % output_dir, regions_exclude)

