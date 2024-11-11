import os
import nrrd
import numpy as np
from regions import generate_region_mask 
from erode import erode_mask

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# USER SETTINGS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Brain regions for quantification (using ABA nomenclature) # see http://atlas.brain-map.org/atlas?atlas=2
#brain_regions_include = ['Hippocampal formation', 'Isocortex', 'Thalamus', 'Hypothalamus', 'Cerebellum', 'Midbrain', 'Hindbrain']  # last one is brain stem
brain_regions_include = ['Hippocampal formation', 'Isocortex', 'Thalamus', 'Hypothalamus', 'Midbrain', 'Hindbrain']  # last one is brain stem

# Brain regions to exclude
brain_regions_exclude = ['Main olfactory bulb', 'Accessory olfactory bulb', 'Anterior olfactory nucleus', 'Taenia tecta', 'ventricular systems']

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

    regions_include = generate_region_mask(output_dir, "atlas_regions_include", brain_regions_include, resolution)
    regions_exclude = generate_region_mask(output_dir, "atlas_regions_exclude", brain_regions_exclude, resolution)

    mask_regions_exclude_with_erosion = erode_mask(regions_exclude, "%s/tmp")
    nrrd.write("%s/atlas_regions_exclude_eroded.nrrd" % output_dir, mask_regions_exclude_with_erosion)

    # Combine into a single mask
    mask = np.zeros(np.shape(mask_regions_exclude_with_erosion))
    mask[:,:,:] = regions_include[:,:,:]
    #mask[mask_regions_exclude_with_erosion==1] = 0
    mask[regions_exclude>0] = 0
    nrrd.write("%s/selected_atlas_areas.nrrd" % output_dir, mask)

