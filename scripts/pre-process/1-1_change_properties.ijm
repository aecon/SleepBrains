/*ImageJ macro building upon 3_segment_plaques by labelling objects and providing information about oject characteristics via MorphoLibJ
 * requires setting Plugins > Bio-Formats > Bio-Formats Plugins Configuration > Formats > Fei TIFF: enabled and windowless checked //TODO: add all other Tiffs, here and makeNrrd
 * written by Lisa Polzer
 */
 
//TODO: look at "FutureDev:" //FutureDev: produce a debugging mode excluding the cropping parts, including all the "for troubleshooting" print statements
input_directory= "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/";
//input_directory = "/media/user/SSD1/Athena/Data/test/";

ch0 = "488";
ch1 = "647";

directories = getFileList(input_directory);
Ndir = directories.length;

setBatchMode(true);
// Loop over sample directories
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);

	// Find channel files inside the directory
	files = getFileList(input_directory + directories[i]);
	Array.print(files);
	Nfiles = files.length;
	print("Number of files in directory:", Nfiles);

    // Check if the directory startsWith any files with the word "segmented"
    startsWith_cropped = false;
    for (j = 0; j < Nfiles; j++) {
        if (files[j].startsWith("cropped")) {
            startsWith_cropped = true;
            break; // Stop checking once we find a "segmented" file
        }
    }

    // If no "segmented" files are found, skip this directory
    if (!startsWith_cropped) {
        print("Skipping directory (does not contain any 'segmented' files):", directories[i]);
        continue; // Skip to the next directory
    }

	// Find filepaths of 488 and 647 chanels
	for(j=0; j<Nfiles; j++){
		if (files[j].startsWith("cropped_") && files[j].contains(ch0)) {
			file_ch0 = files[j];
			path_ch0 = input_directory + directories[i] + files[j];
		}
		if (files[j].startsWith("cropped_") && files[j].contains(ch1)) {
			file_ch1 = files[j];
			path_ch1 = input_directory + directories[i] + files[j];
		}
		if (files[j].startsWith("labelled_") && files[j].contains(ch0)) {
			file_labelled = files[j];
			path_labelled = input_directory + directories[i] + files[j];
		}
	}
	print("  ", "Channel 1:", path_ch0);
	print("  ", "Channel 2:", path_ch1);
	
	//path 0 cropped image: open image
	open(path_ch0); //print("Opening cropped highRes.tif from: " + outputDirectory + filename + "highRes_cropped.raw"); //for troubleshooting
	titlecropped = getTitle();
	sliceNumber = nSlices;

	//path 0 cropped image: change image properties, replace image with corrected version
	run("Properties...", "channels=1 slices=" + sliceNumber + " frames=1 pixel_width=3.2600 pixel_height=3.2600 voxel_depth=3.0000");
	resave_path = input_directory + directories[i] + titlecropped; 
	run("Nrrd ... ", "nrrd=["+resave_path+"]");

	//cleanup windows
	close("*");


	//path 1 cropped image: open image
	open(path_ch1); //print("Opening cropped highRes.tif from: " + outputDirectory + filename + "highRes_cropped.raw"); //for troubleshooting
	titlecropped = getTitle();
	sliceNumber = nSlices;

	//path 1 cropped image: change image properties, replace image with corrected version
	run("Properties...", "channels=1 slices=" + sliceNumber + " frames=1 pixel_width=3.2600 pixel_height=3.2600 voxel_depth=3.0000");
	resave_path = input_directory + directories[i] + titlecropped; 
	run("Nrrd ... ", "nrrd=["+resave_path+"]");

	//cleanup windows
	close("*");

	/*
	//labelled image: open image
	open(path_labelled); //print("Opening cropped highRes.tif from: " + outputDirectory + filename + "highRes_cropped.raw"); //for troubleshooting
	titlelabelled = getTitle();
	sliceNumber = nSlices;

	//labelled image: change image properties, replace image with corrected version
	run("Properties...", "channels=1 slices=" + sliceNumber + " frames=1 pixel_width=3.2600 pixel_height=3.2600 voxel_depth=3.0000");
	resave_path = input_directory + directories[i] + substring(titlelabelled, 0, lengthOf(titlelabelled)-13) + ".nrrd"; 
	run("Nrrd ... ", "nrrd=["+resave_path+"]");

	//cleanup windows
	close("*");
	*/
}

print("\nFinished correcting image properties!\n");
