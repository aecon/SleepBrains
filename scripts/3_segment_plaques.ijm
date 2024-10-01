/*ImageJ macro using .nrrds from macro makeNrrd output
 * requires setting Plugins > Bio-Formats > Bio-Formats Plugins Configuration > Formats > Fei TIFF: enabled and windowless checked //TODO: add all other Tiffs, here and makeNrrd
 * written by Lisa Polzer
 */
 
//TODO: look at "FutureDev:" //FutureDev: produce a debugging mode excluding the cropping parts, including all the "for troubleshooting" print statements
input_directory= "/media/user/SSD1/Athena/Data/REUS_VENAD_TREVC_Desiree/";
//input_directory = "/media/user/SSD1/Athena/Data/test/";

ch0 = "488";
ch1 = "647";

directories = getFileList(input_directory);
Ndir = directories.length;

// Loop over sample directories
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);

	// Find channel files inside the directory
	files = getFileList(input_directory + directories[i]);
	Array.print(files);
	Nfiles = files.length;
	print("Number of files in directory:", Nfiles);

	// Find filepaths of 488 and 647 chanels
	for(j=0; j<Nfiles; j++){
		if (files[j].contains("cropped_") && files[j].contains(ch0)) {//TODO:use startswith
			file_ch0 = files[j];
			path_ch0 = input_directory + directories[i] + files[j];
		}
		if (files[j].contains("cropped_") && files[j].contains(ch1)) {
			file_ch1 = files[j];
			path_ch1 = input_directory + directories[i] + files[j];
		}
	}
	print("  ", "Channel 1:", path_ch0);
	print("  ", "Channel 2:", path_ch1);
	
	 
	//opens and duplicates image for use in two thresholding steps
	run("Brightness/Contrast...");
	open(path_ch0); //print("Opening cropped highRes.tif from: " + outputDirectory + filename + "highRes_cropped.raw"); //for troubleshooting
	titleCropped = getTitle();
	//print(" > Duplicating stack");  //for troubleshooting
	run("Duplicate...", "title=titleIclip duplicate");
	titleIclip="titleIclip";
	
	
	//threshold 1: excluding very bright artefacts & cell clusters
		//intensity clipping
		selectWindow(titleIclip);
		run("Threshold..."); //TODO: set default: don't reset range
		waitForUser("Intensity clip for Background Normalization:\nUse the threshold to find the minimum intensity that captures bright spots/artefacts to be excluded from background estimation.\nDo so by adjusting the top bar exclusively, adjust B&C if necessary.\n \nClick 'OK' when done.");
		Imax = getNumber("Fill in the minimum foreground intensity:", 5000);
		//print(" > Clipping intensity"); //for troubleshooting
		run("Max...", "value=" + Imax + " stack");
		//print(" > Intensity clipped to " + Imax); //for troubleshooting
		
		//duplicates stack: blur with sigma=1
		selectWindow(titleIclip);
		//print(" > Duplicating stack with clipped maximum intensity"); //for troubleshooting
		run("Duplicate...", "title=small_blur duplicate");
		small_blur="small_blur";
		
		//foreground smoothing
		selectWindow(small_blur);
		smallSigma = 2;
		run("Gaussian Blur 3D...", "x="+smallSigma+" y="+smallSigma+" z="+smallSigma); //TODO: adjustblur 10-100, pot. create mask (from alignment) and only consider pixels inside, or reflect at border
		//print(" > Gaussian smoothing, sigma="+smallSigma+" completed."); //for troubleshooting

		//background smoothing
		selectWindow(titleIclip); //TODO: pot. add laplacian to add sharper edges to make cells more easily detectable
		bigSigma=15.25; //TODO: adjustblur 10-100, pot. create mask (from alignment) and only consider pixels inside, or reflect at border
		//print(" > Running background smoothing."); //for troubleshooting
		run("Gaussian Blur 3D...", "x="+bigSigma+" y="+bigSigma+" z="+bigSigma);
		//print(" > Gaussian smoothing of background (sigma="+bigSigma+") completed."); //for troubleshooting

		//background bormalization
		//print("(d) Intensity normalization."); //for troubleshooting
		//print(" > Dividing by background."); //for troubleshooting
		imageCalculator("Divide create 32-bit stack", small_blur, titleIclip);

		//get rid of background
		titleNorm = getTitle();
		//print(" > Intensity normalization (dividing by background) completed."); //for troubleshooting
		selectWindow(titleCropped);
		run("Duplicate...", "duplicate");
		waitForUser("Foreground ID.\nMark complete foreground red. \nClick 'OK' when done.");
		getThreshold(lower, upper);
		setThreshold(lower, upper);
		setOption("BlackBackground", true);
		run("Convert to Mask", "method=Default background=Default black");
		rename("MASK_"+titleCropped);
		title_mask = getTitle();
		imageCalculator("Multiply create stack", titleNorm, title_mask);
		titleNorm = getTitle();
		
		//closing background and cropped
		selectWindow(titleCropped);
		close();
		selectWindow(small_blur); //TODO: should mask inner be duplicated from small blur?
		close();
		selectWindow(titleIclip);
		close();
		//print("(e) Intensity thresholding: foreground selection."); //for troubleshooting

		// Store segmented cells
		//print("(h) Segmented foreground."); //for troubleshooting
		selectWindow(titleNorm);
		normal_path = input_directory + directories[i] + "normal_" + file_ch0;
		//print(" > Storing segmented foreground as 8bit raw file in:" + segmented_path); //for troubleshooting
		run("Nrrd ... ", "nrrd=["+normal_path+"]");
	
	
	//threshold 2: including candidate cells
		//duplicating stack
		//selectWindow(titleNorm);
		//print(" > Duplicating normalized stack."); //for troubleshooting
		run("Duplicate...", "title=mask_inner duplicate");
		mask_inner = "mask_inner";
		
		//threshold on normalized intensity
		//print(" > Setting normalized intensity theshold."); //for troubleshooting
		selectWindow(mask_inner);
		waitForUser("Use the threshold to find the minimum cell intensity.\n \nClick 'OK' when done.");
		getThreshold(lower, upper);
		setThreshold(lower, upper);
		setOption("BlackBackground", true);
		selectWindow(mask_inner);
		//print(" > Converting thresholded image to mask."); //for troubleshooting
		run("Convert to Mask", "method=Default background=Default black");
		
		//store candidate cells
		title_segmented = getTitle();
		selectWindow(title_segmented);
		segmented_path = input_directory + directories[i] + "segmented_" + file_ch0; //TODO: remove prev. titles
		//print(" > Storing segmented foreground as 8bit raw file in:" + segmented_path); //for troubleshooting
		run("Nrrd ... ", "nrrd=" + segmented_path);
		
		// Filter on particle size //TODO: ggf. replace this paragraph
		//print("(g) Filtering very small (<10), very large (>1500), and non-circular particles."); //for troubleshooting
		selectWindow(title_segmented);
		run("Analyze Particles...", "size=200-10000 circularity=0.75-1.00 show=Masks clear include stack"); //TODO: show user the max. size for particles, pot. use 
		title_candidates = getTitle();
		
		selectWindow(title_candidates);
		//close();
		setOption("ScaleConversions", true); //converts segmented image from 8 to 16 bits to match other files' types
		run("16-bit"); 
		
		// Store segmented cells
		//print("(h) Segmented foreground."); //for troubleshooting
		selectWindow(title_candidates);
		//input_directory = "/media/user/SSD1/Athena/Data/REUS_VENAD_TREVC_Desiree/Brain10_stitched" //TODO:remove!!!!!
		plaques_path = input_directory + directories[i] + "plaques_" + file_ch0; //TODO: remove prev. titles
		//print(" > Storing segmented foreground as 8bit raw file in:" + segmented_path); //for troubleshooting
		run("Nrrd ... ", "nrrd=" + plaques_path);
	
	close("*");

}

//gets list of currently open windows, closes all but the log
windows = getList("window.titles"); //Array.print(windows) //for troubleshooting
/*Array.print(windows); //Log, B&C, Threshold
for (i = 0; i < windows.length; i++) {
	close(windows[i]); //TODO: fix: i.e. don't close log
}*/

print("\nFinished running macro 'workNrrd'!\n");