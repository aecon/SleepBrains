input_directory= "/media/user/SSD1/Athena/Data/REUS_VENAD_TREVC_Desiree/";
//input_directory= "/media/user/SSD1/Athena/Data/test/";

ch0 = "488";
ch1 = "647";

directories = getFileList(input_directory);
Ndir = directories.length;

// Loop over sample directories
for(i=0; i<Ndir; i++){
	print("Processing directory", i+1, "/", Ndir, ":", directories[i]);

	// Find channel files inside the directory
	files = getFileList(input_directory + directories[i]);
	Nfiles = files.length;
	print("Number of files in directory:", Nfiles);

	// Find filepaths of 488 and 647 chanels
	for(j=0; j<Nfiles; j++){
		if (files[j].contains("original_") && files[j].contains(ch0)) {
			file_ch0 = files[j];
			path_ch0 = input_directory + directories[i] + files[j];
		}
		if (files[j].contains("original_") && files[j].contains(ch1)) {
			file_ch1 = files[j];
			path_ch1 = input_directory + directories[i] + files[j];
		}
	}
	print("  ", "Channel 1:", path_ch0);
	print("  ", "Channel 2:", path_ch1);


	/*
	 *  Load first channel
	 */
	 
	open(path_ch0);
	slices = nSlices;
	run("Brightness/Contrast...");

	// CROPPING
	// xy-cropping
	setTool("rectangle");
	waitForUser("xy-Cropping", "On 520 image:\n\nMake an xy selection and note slices to keep for z-cropping and whether flips are needed.\n\nPress 'OK' when done.");
	Roi.getBounds(x, y, width, height);
	run("Crop");

	// z-cropping
	Dialog.create("z-Cropping");
	Dialog.addNumber("First Slice:",1);
	Dialog.addNumber("Last Slice:",slices);
	Dialog.show();
	firstSlice = Dialog.getNumber();
	lastSlice = Dialog.getNumber();
	run("Slice Keeper", "first="+firstSlice+" last="+lastSlice+" increment=1");

	// FLIPPING: Flip stack to match orientation of Allen Brain Atlas.
	// depth and horizontal flipping
	// open the dialogue for image flippling
	Dialog.create("Flips if needed");
	Dialog.addNumber("Give 1 to flip z-stack, 0 to NOT flip:",0);
	Dialog.addNumber("Give 1 to flip horizontally, 0 to NOT flip:",0);
	Dialog.show();
	flipZ = flip_ZStack();
	flipH = flipHorizontally();

	// saving cropping info in file
	correctionsInfo_path = input_directory + directories[i] + "cropping_info.txt";
	print(correctionsInfo_path);
	correctionsInfo = File.open(correctionsInfo_path);
	print(correctionsInfo, "filename\t\tx0\t\ty0\t\twidth\t\theight\t\tfirstSlice\t\tlastSlice\t\tflipZ\t\tflipH");
	print(correctionsInfo, file_ch0+"\t\t"+x+"\t\t"+y+"\t\t"+width+"\t\t"+height+"\t\t"+firstSlice+"\t\t"+lastSlice+"\t\t"+flipZ+"\t\t"+flipH);
	File.close(correctionsInfo);

	// save cropped ch0 file
	output_path = input_directory + directories[i] + "cropped_" + file_ch0;
	run("Nrrd ... ", "nrrd=" + output_path);
	
	// Close open ch0 files
	run("Close All");


	/*
	 *  Load second channel
	 */

	// load second channel image
	open(path_ch1);
	SecondChannelID = getTitle();
	selectWindow(SecondChannelID);
		
	// apply xyz-crop onto second channel
	makeRectangle(x, y, width, height);
	run("Crop");
	run("Slice Keeper", "first="+firstSlice+" last="+lastSlice+" increment=1");

	// flip stack to match orientation of Allen Brain Atlas.
	if(parseFloat(flipZ)==1){
		run("Flip Z");
	}
	if(parseFloat(flipH)==1){
		run("Flip Horizontally", "stack");
	}
	
	// save cropped ch1 file
	output_path = input_directory + directories[i] + "cropped_" + file_ch1;
	run("Nrrd ... ", "nrrd=" + output_path);

	// close all files
	run("Close All");
}

print("DONE.");
exit;



/*
 * Helper functions 
 */
 
function flip_ZStack() {
	// Z-Stack flip: start with outer (round) part of brain (not cut half-brain) 
	flipZ = Dialog.getNumber;
	print("  flipZ:", flipZ);
	if(parseFloat(flipZ)==1){
		run("Flip Z");
	}
	return flipZ;
}

function flipHorizontally() {
	// Horizontal flip: cerebellum on the left
	flipH = Dialog.getNumber;
	print("  flipH:", flipH);
	if(parseFloat(flipH)==1){
		run("Flip Horizontally", "stack");
	}
	return flipH;
}