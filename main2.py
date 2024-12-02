import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QWidget, QFileDialog,
    QLineEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QGridLayout
)
import numpy as np
from matplotlib import pyplot as plt
from tifffile import imsave, imwrite
from PIL import Image
import imagej
import scyjava as sj
import shutil

#global variables
px_x=0
px_y=0
z_slices=0
bytes_before_images=0
bytes_between_images=0

#control variables
raw_to_16bit=False
raw_to_8bit=False
raw_to_8bit_dnzd=False

#variables to track the directories, created or old
#NOTE: User can choose not to use this funcionalty, and so these dirs will not be made
working_dir=os.getcwd
u8bit_dir=""
u8bit_dns_dir=""
tiff_dir=""

#variables for tif_conv
file_names=list()

#def macro_func():


#setting directory
def get_directory():
    global working_dir 
    working_dir = QFileDialog.getExistingDirectory(None, 'Select Directory')
    cwd_label_txt = "Current Directory: " + str(working_dir)
    cwd_label.setText(cwd_label_txt)

def run():
     
    create_dirs()

    #if(raw_to_16bit or raw_to_8bit or raw_to_16bit):
    #    get_files_working_dir()
    #    if(raw_to_8bit) : conv_8bit_tiff()
    #    if(raw_to_16bit) : conv_16bit_tiff()

    # get image file paths
    get_files_working_dir()

    # convert images
    if raw_to_8bit:
        for f in file_names:
            raw_to_tiff(f, px_x, px_y, 8)
    if raw_to_16bit:
        for f in file_names:
            raw_to_tiff(f, px_x, px_y, 16)

    sys.exit()


def raw_to_tiff(path: str, x: int, y: int, bit_depth: int):
    """
    """
    # import java/imagej resources
    FileInfo = sj.jimport('ij.io.FileInfo')
    Raw = sj.jimport('ij.plugin.Raw')
    IJ = sj.jimport('ij.IJ')

    # create file info
    fi = FileInfo()
    # populate file info with metadata
    if bit_depth == 8:
        fi.fileType = FileInfo.GRAY8
    if bit_depth == 16:
        fi.fileType = FileInfo.GRAY16_SIGNED
    
    fi.offset=0
    fi.width = x
    fi.height = y
    fi.nImages=955
    fi.gapBetweenImages=0
    fi.intelByteOrder=True
    fi.pixelWidth = 1                   # Voxel size in x direction
    fi.pixelHeight = 1                  # Voxel size in y direction
    fi.pixelDepth = 1                   # Voxel size in z direction
    fi.unit = "pixel"                   # Unit of voxel size
    fi.valueUnit = ""                   # No specific unit for values
    fi.calibrationFunction = 0          # LUncalibrated
    fi.whiteIsZero = False              # White is not zero

    print(f"Width: {fi.width}, Height: {fi.height}, Bit Depth: {bit_depth}, Byte Order: {'Little' if fi.intelByteOrder else 'Big'}")

    # open imp with Raw and file info
    imp = Raw.open(path, fi)

    if bit_depth == 16:
        IJ.run(imp, "Enhance Contrast", "saturated=0.35")  # Adjust for better visualization


    # TODO: extract file name
    name=path[:len(path) - len(".raw")] + '_8bit.tif'

    # save Imp to disk as tiff
    ij.IJ.saveAs(imp,"tiff", name)


def set_paramaters(x_pixel_input:int,  y_pixels_input :int,  z_slices_input :int,bytes_before_img_input :int, bytes_between_img_input:int):
    """
    Sets all the parameters needed for processing raw images

    """
    global px_x, px_y, z_slices, bytes_before_images, bytes_between_images

    px_x=x_pixel_input
    px_y=y_pixels_input
    z_slices=z_slices_input
    bytes_before_images=bytes_before_img_input
    bytes_between_images=bytes_between_img_input

def set_controls( u16_bit_conv,u8_bit_conv, u8_bit_conv_dnzd):
    """
    Sets all the control variables for the flow of the progra, specifgying which processes are carried out
    
    """
    global raw_to_16bit, raw_to_8bit, raw_to_8bit_dnzd

    raw_to_16bit=u16_bit_conv
    raw_to_8bit=u8_bit_conv
    raw_to_8bit_dnzd=u8_bit_conv_dnzd


def create_dirs():
    """
    Creates directories to store processed files as per the controls set
    
    """
    global raw_to_16bit, raw_to_8bit, raw_to_8bit_dnzd
    global tiff_dir, u8bit_dir, u8bit_dns_dir

    if(raw_to_16bit):
        if os.path.exists(working_dir+'/TIFF_FILES') == False:
           os.mkdir(working_dir+'/TIFF_FILES')
        tiff_dir=os.path.join(working_dir,'TIFF_FILES')

    if(raw_to_8bit):
        if os.path.exists(working_dir+'/DOWNSIZED') == False:
            os.mkdir(working_dir+'/DOWNSIZED')
        u8bit_dir=os.path.join(working_dir,'DOWNSIZED')

    if(raw_to_8bit_dnzd):
        if os.path.exists(working_dir+'/DOWNSIZED/RESIZED') == False:
            os.mkdir(working_dir+'/DOWNSIZED/RESIZED')
        u8bit_dns_dir=os.path.join(working_dir,'/DOWNSIZED/RESIZED')


def get_files_working_dir():
    """
    Creates a list of all the raw files in the current working directory
    
    """
    global file_names
    for file in os.listdir(working_dir):
        if file.endswith('.raw') and not file.startswith('._'):
            file_name=os.path.normpath(os.path.join(working_dir, file))
            file_names.append(file_name)


def conv_8bit_tiff():
    """
    Converts files in the files_names to 8 bit tiff images and stores them in the 'DOWNSIZED' folder
    
    """

    global file_names

    img_shape = np.array((px_x,px_y,z_slices), dtype = np.uint)
    img = np.zeros(img_shape, dtype=np.uint16)

    for file in file_names:
        img=np.zeros(img_shape,dtype = np.uint16)
        # Read the 16-bit pixel data from the file
        px_data = np.fromfile(file, dtype=np.uint16)
        px_data = px_data[int(bytes_before_images/2):]
            
        for i in range(0,z_slices):
            i_start_index = i * (px_x * px_y + int(bytes_between_images / 2))
            i_end_index = i_start_index + (px_x * px_y)
                    
            px_data_i = px_data[i_start_index:i_end_index]
            img_i = px_data_i.reshape(px_y, px_x)
            img_i_r=Image.fromarray(img_i)
            
            # Store the slice in the img array
            img[:, :, i] = np.array(img_i_r, dtype=np.uint16)

        #Bit-shifting to 8-bit
        img = (img >> 8).astype('uint8')

        print(img.size)

        # Save the 8-bit image
        bit8_file_name=file[:len(file) - len(".raw")] + '_8bit.tif'
        imwrite(bit8_file_name, np.moveaxis(img,2, 0))
        shutil.move(bit8_file_name,u8bit_dir)

def conv_8bit__dnsd_tiff():
    """
    Converts files in the files_names to 8 bit tiff images downsized to 50% of the size and stores them in the 'DOWNSIZED' folder
    
    """

    global file_names

    img_shape = np.array((px_x,px_y,z_slices), dtype = np.uint)
    img = np.zeros(img_shape, dtype=np.uint16)

    for file in file_names:
        img=np.zeros(img_shape,dtype = np.uint16)
        # Read the 16-bit pixel data from the file
        px_data = np.fromfile(file, dtype=np.uint16)
        px_data = px_data[int(bytes_before_images/2):]
            
        for i in range(0,z_slices):
            i_start_index = i * (px_x * px_y + int(bytes_between_images / 2))
            i_end_index = i_start_index + (px_x * px_y)
                    
            px_data_i = px_data[i_start_index:i_end_index]
            img_i = px_data_i.reshape(px_y, px_x)
            img_i_r=Image.fromarray(img_i)
            
            # Store the slice in the img array
            img[:, :, i] = np.array(img_i_r, dtype=np.uint16)

        #Bit-shifting to 8-bit
        img = (img >> 8).astype('uint8')

        print(img.size)

        # Save the 8-bit image
        bit8_file_name=file[:len(file) - len(".raw")] + '_8bit.tif'
        imwrite(bit8_file_name, np.moveaxis(img,2, 0))
        shutil.move(bit8_file_name,u8bit_dir)


def conv_16bit_tiff():
    """
    Converts files in the files_names to 16 bit tiff images and stores them in the 'TIFF' folder
    
    """
    print("here")
    img_shape = np.array((px_y,px_x,z_slices), dtype = np.uint)
    img=np.zeros(img_shape,dtype = np.uint16)
    for file in file_names:
        px_data = np.fromfile(file, dtype = np.uint16)
        px_data = px_data[int(bytes_before_images/2):]
        
        for i in range (0,z_slices):
        
            i_start_index=i*(px_x*px_y+int(bytes_between_images/2))
            i_end_index=i_start_index+(px_x*px_y)
                                          
            px_data_i=px_data[i_start_index:i_end_index]
            img_i=(px_data_i.reshape(int(px_y),int(px_x)))
            
            img[:,:,i]=img_i

        #saving and storing files in assigned directory
        bit16_file_name=file[:len(file) - len('.raw')] + '.tif'
        imwrite(bit16_file_name, np.moveaxis(img, 2, 0))
        shutil.move(bit16_file_name,tiff_dir)

    else:
        pass


#FROM UI INPUTS
if __name__ == "__main__":
    # initialize imagej
    ij = imagej.init('sc.fiji:fiji', mode='interactive')
    print(f"Fiji version: {ij.getVersion()}")

    # things run here
    # Initialize the application
    app = QApplication(sys.argv)

    # Create the main window
    window = QWidget()
    window.setWindowTitle("Processingv11")
    window.resize(600, 400)

    # Create a layout
    main_layout = QVBoxLayout()

    # Current directory label and button
    cwd_label_txt = "Current Directory: //CWD//"
    cwd_label = QLabel(cwd_label_txt)

    select_dir_button = QPushButton("Select Directory")
    select_dir_button.clicked.connect(get_directory)

    # Add directory selection to layout
    main_layout.addWidget(cwd_label)
    main_layout.addWidget(select_dir_button)

    # Create the parameters section
    params_layout = QGridLayout()
    params_layout.addWidget(QLabel("Parameters for TIF Conversion"), 0, 0, 1, 2)

    bytes_between_images_input=0
    params_layout.addWidget(QLabel("Bytes between images:"), 1, 0)
    bytes_between_images_input_line =QLineEdit()
    params_layout.addWidget(bytes_between_images_input_line, 1, 1)

    bytes_before_images_input=0
    params_layout.addWidget(QLabel("Bytes before images:"), 2, 0)
    bytes_before_images_input_line = QLineEdit()
    params_layout.addWidget(bytes_before_images_input_line, 2, 1)

    pixel_size_x_input=0
    params_layout.addWidget(QLabel("Pixel size (x):"), 3, 0)
    pixel_size_x_input_line = QLineEdit()
    params_layout.addWidget(pixel_size_x_input_line, 3, 1)

    pixel_size_y_input=0
    params_layout.addWidget(QLabel("Pixel size (y):"), 4, 0)
    pixel_size_y_input_line = QLineEdit()
    params_layout.addWidget(pixel_size_y_input_line, 4, 1)

    z_slices_input=0
    params_layout.addWidget(QLabel("Z slices:"), 5, 0)
    z_slices_input = QLineEdit()
    params_layout.addWidget(z_slices_input, 5, 1)

    param_dir_button = QPushButton("Set Parameters")
    param_dir_button.clicked.connect( lambda: set_paramaters(int(pixel_size_x_input_line.text()),int(pixel_size_y_input_line.text()),int(z_slices_input.text()),int(bytes_before_images_input_line.text()),int(bytes_between_images_input_line.text())))


    # Add parameters layout to main layout
    main_layout.addLayout(params_layout)

    main_layout.addWidget(param_dir_button)

    # Create the radio buttons for conversion options
    steps_layout = QVBoxLayout()
    steps_label = QLabel("Choose steps to perform")

    convert_16bit_radio = QCheckBox("Convert RAW files to 16bit")
    convert_8bit_radio = QCheckBox("Convert RAW files to 8bit")
    resize_8bit_radio = QCheckBox("Downsample 8bit tif files by 50%")

    steps_layout.addWidget(steps_label)
    steps_layout.addWidget(convert_16bit_radio)
    steps_layout.addWidget(convert_8bit_radio)
    steps_layout.addWidget(resize_8bit_radio)

    
    steps_dir_button = QPushButton("Set Steps")
    steps_dir_button.clicked.connect( lambda: set_controls(convert_16bit_radio.isChecked(),convert_8bit_radio.isChecked(),resize_8bit_radio.isChecked()))
    steps_layout.addWidget(steps_dir_button)

    # Add radio button section to main layout
    main_layout.addLayout(steps_layout)

    
    #TODO RUN BUTTON

    run_button = QPushButton("Run")
    run_button.clicked.connect(run)
    run_button.setStyleSheet("background-color: '#b6e6fc'")
    main_layout.addWidget(run_button)

    # Set the layout to the main window
    window.setLayout(main_layout)

    # Show the window
    window.show()


    # Run the application
    sys.exit(app.exec_())