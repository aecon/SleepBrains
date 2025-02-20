import os
import nrrd
import numpy as np
from regions import generate_region_mask 
#from erode import erode_mask
from scipy.ndimage import binary_erosion

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
    print(regions_include.shape)
    print(np.unique(regions_include))
    print(regions_exclude.shape)
    print(np.unique(regions_exclude))

    # Erode selected (included) regions to exclude FP signal at the edge of the regions
    eroded_regions_include = np.zeros(regions_include.shape)
    for i in range(len(brain_regions_include)):
        idx = regions_include==i+1
        region = np.zeros(regions_include.shape)
        region[idx] = 1
        eroded_region = binary_erosion(region, iterations=2)
        eroded_regions_include[eroded_region>0] = i+1

    # Combine into a single mask
    mask = np.zeros(regions_include.shape)
    mask[:,:,:] = eroded_regions_include[:,:,:]
    mask[regions_exclude>0] = 0
    nrrd.write("%s/selected_atlas_areas.nrrd" % output_dir, mask)

