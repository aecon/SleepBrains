input_directory= "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/";

directories = getFileList(input_directory);
Ndir = directories.length;

setBatchMode(true);
// Loop over sample directories
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);

	// Path to aligned atlas file
	atlas_file = input_directory + directories[i] + "align/elastix_bspline/result.0.nrrd";
	
	// Path to raw file
	// - Find files inside the directory
	files = getFileList(input_directory + directories[i]);
	Nfiles = files.length;
	print("Number of files inside directory:", Nfiles);
	// - Loop over files
	for(j=0; j<Nfiles; j++){
		if (matches( files[j], "cropped_original_.*")) {
			if (matches( files[j], ".*_ch_0.tif.nrrd")) {
				raw_file = input_directory + directories[i] + files[j];
			}			
		}
	}
	
	// Load atlas file + convert to 8bit
	open(atlas_file);
	// remove layer of very high values on atlas perimeter
	// https://forum.image.sc/t/replacing-all-pixels-in-a-roi-selection-by-a-value-of-0-one-unique-pixel-value/37525/2
	// changeValues(v1, v2, v3)
	// Changes pixels in the image or selection that have a value in the range v1 - v2 to v3 
	for (k=1; k<nSlices+1;k++) {
		Stack.setSlice(k); 
		//print("Slice number = "+k); //Just to check the slice number
		changeValues(65000,65535,0);
	}
	title_Atlas = getTitle();
	// reslice
	//run("Reslice [/]...", "output=1 start=Top rotate avoid");
	run("Enhance Contrast", "saturated=0.35");
	setMinAndMax(0, 255);
	
	// Load data + convert to 8bit
	open(raw_file);
	run("Enhance Contrast", "saturated=0.35");
	resetMinAndMax();
	title_Data = getTitle();
	// reslice
	//run("Reslice [/]...", "output=1 start=Top rotate avoid");
	run("Enhance Contrast", "saturated=0.35");
	setMinAndMax(0, 255);

	// Merge channels
	run("Merge Channels...", "c1=["+title_Data+"] c2=["+title_Atlas+"] create ignore");
	title_Merge = getTitle();

	// Make montage
	//slices = nSlices;
	//nColumns = 10;
	//start = 100;
	//increment = floor((slices-start)/(nColumns-1));
	//run("Make Montage...", "columns="+nColumns+" rows=1 scale=1 first="+start+" increment="+increment+" border=10");
	//title_Montage = getTitle();

	// Save montage
	selectImage(title_Merge);
	brain_ID = substring(directories[i], 0, lengthOf(directories[i])-1);
	output_path = input_directory + directories[i] + "overlay_raw_alignedAtlas_" + brain_ID + ".tif";
	saveAs("Tiff", output_path);

	// Close images
	run("Close All");
	
}
print("DONE.");
setBatchMode(false);
