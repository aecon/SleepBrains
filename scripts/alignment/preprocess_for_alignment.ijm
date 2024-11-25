input_directory= "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/";
//input_directory= "/media/user/SSD1/Athena/Data/PROJECT_SLEEP_2024-09/test/";

ch0 = "488";
ch1 = "647";

directories = getFileList(input_directory);
Ndir = directories.length;

// Parameters
downsize_factor = 2;
sigmaAlign = 2;


// Loop over brain directories
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);

	if ( startsWith(directories[i],"Brain") ){

        // Find channel files inside the directory
        files = getFileList(input_directory + directories[i]);
        Nfiles = files.length;
        print("Number of files in directory:", Nfiles);

        // Find filepath of 488 chanel
        counter = 0;
        basename = 0;
        for(j=0; j<Nfiles; j++){
        	if ( startsWith(files[j],"cropped_original_Brain") && files[j].contains(ch0) ) {
            	file_ch0 = files[j];
            	path_ch0 = input_directory + directories[i] + files[j];
            	counter = counter + 1;
            	basename = files[j];
            }
        }
        if (counter != 1) {
        	print("Found incorrect number of files. Exiting...");
        	exit;
        }
        print("  ", "-File:", path_ch0);

		// Check if file does not exist
		output_path = input_directory + directories[i] + "prealignment_" + basename;
		if (File.exists(output_path)){
			print("File exists:", output_path);
		}
		else {

	        // Load data
	        print("  ", "-Loading the data...");
	        open(path_ch0);
	        slices = nSlices;
	        run("Brightness/Contrast...");

			// Downsize by factor of 2
			print("  ", "-Downsizing the data...");
	        run("Bin...", "x="+downsize_factor+" y="+downsize_factor+" z="+downsize_factor+" bin=Average"); //alternative: "scale" | Dont use "size"!
			title2 = getTitle();

	        // Threshold: Cap the intensity of few very bright pixels. Should not cover continuous areas of the sample!
	        selectWindow(title2);
	        // - find intensity for cap
	        run("Threshold...");
	        waitForUser("Choose max intensity for alignment cap. Scroll through the stack to check that no continuous areas are selected.\n\nClick 'OK' when done.");
	        Imax = getNumber("Intensity:", 800);
	        // - cap intensity
	        print("  ", "-Capping the intensity...");
	        run("Max...", "value=" + Imax + " stack");
			titleCap = getTitle();

			// Smooth to remove fine-scale structures (cells, etc)
			print("  ", "-Blurring...");
			run("Gaussian Blur 3D...", "x="+sigmaAlign+" y="+sigmaAlign+" z="+sigmaAlign); //blur decreases noise for better slignment

	        // save cropped file
	        print("  ", "-Output path:", output_path);
	        run("Nrrd ... ", "nrrd=" + output_path);

	        // close all files
	        run("Close All");

		}
        
	}
}

print("DONE.");
exit;

