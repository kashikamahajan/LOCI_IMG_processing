/*
 * Rough draft for downsampling 2GB images into 128x128x128 cubes.
 * Future iterations should take into account size metadata for accurate isotropic voxels
 */

#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix

// See also Process_Folder.py for a version of this code
// in the Python scripting language.
setBatchMode("hide");
processFolder(input);

// function to scan folders/subfolders/files to find files with correct suffix
function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, output, list[i]);
	}
}

function processFile(input, output, file) {
	// Do the processing here by adding your own code.
	open(input + File.separator + file);
	getDimensions(width, height, channels, slices, frames);
	width = floor(width/8);
	height = floor(height/8);
	slices = floor(slices/16);
	run("Size...", "width="+width+" height="+height+" depth="+slices+" constrain average interpolation=Bilinear");
	
	print("Processing: " + input + File.separator + file);
	saveAs("TIFF", output+File.separator+file);
	print("Saving to: " + output);
}
