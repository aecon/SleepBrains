// Parse command-line arguments
arg = getArgument();
arg = split(arg, ",");
input = arg[0];
output = arg[1];

// Load .n5 file
run("HDF5/N5/Zarr/OME-NGFF ... ", "url=n5://file:"+ input +"/?exported_data virtual");

// Save as nrrd
run("Nrrd ... ", "nrrd="+output);

// Close all files and exit
close("*");
run("Quit");