import os
import nrrd
import skimage.io
import numpy as np
from pathlib import Path
from allensdk.core.reference_space_cache import ReferenceSpaceCache

#brain_regions = ['Main olfactory bulb', 'Accessory olfactory bulb', 'Anterior olfactory nucleus', 'Taenia tecta', 'ventricular systems']
#resolution=25

def generate_region_mask(odir, fname, brain_regions, resolution=25):
    """
    Generate a mask of all regions to be excluded.
    """

    print("Downloading atlas...")
    reference_space_key = os.path.join('annotation', 'ccf_2017')

    # Load Reference Space
    rspc = ReferenceSpaceCache(resolution, reference_space_key, manifest=Path(odir) / 'manifest.json')
    tree = rspc.get_structure_tree(structure_graph_id=1) 

    # Get brain region IDs
    print("Retrieving region IDs...")
    main_brain_region_IDs = []
    for _region in brain_regions:
    	_structure = tree.get_structures_by_name([_region])
    	#print('\n', _structure)
    	main_brain_region_IDs.append(_structure[0]['id'])
    print('Main brain region IDs:', main_brain_region_IDs)

    # Download annotation volume
    annotation, meta = rspc.get_annotation_volume()

    # Construct ReferenceSpace
    rsp = rspc.get_reference_space()

    # Remove unassigned structures
    rsp.remove_unassigned()

    # Generate mask for each brain region
    print("Generating masks...")
    all_masks = []
    for _id in main_brain_region_IDs:
    	_mask = rsp.make_structure_mask([_id])
    	all_masks.append(_mask)

    # Reorient masks to saggital ABA view
    reshaped_masks = []
    is_half_brain = True
    for _mask in all_masks:
        Nx, Ny, Nz = np.shape(_mask)   #(528, 320, 456
        if is_half_brain==True:
            Nz = Nz//2
        _tmp = np.zeros((Ny, Nx, Nz))
        for k in range(Nz):
            _tmp[:,:,k] = (_mask[:,:,k]).T
        reshaped_masks.append(_tmp)

    # Save masks as tif files
    #print("Saving individual masks...")
    #for _mask, _region in zip(reshaped_masks, brain_regions):
    #    skimage.io.imsave("%s/mask_%s.tif" % (odir, _region), _mask.T, plugin="tifffile", check_contrast=False)

    # Exclude masked brain regions
    all_areas_to_be_excluded = np.zeros(np.shape(reshaped_masks[0]))
    for i, _mask in enumerate(reshaped_masks):
        all_areas_to_be_excluded[_mask==1] = i+1

    # Save nrrd file
    print("Saving combined mask...")
    nrrd.write("%s/%s.nrrd" % (odir, fname), all_areas_to_be_excluded)

    return all_areas_to_be_excluded
 
