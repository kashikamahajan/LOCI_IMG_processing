
import sys
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QWidget, QFileDialog,
    QLineEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QGridLayout
)


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


#def macro_func():


#setting directory
def get_directory():
    working_dir = QFileDialog.getExistingDirectory(None, 'Select Directory')
    cwd_label_txt = "Current Directory: " + str(working_dir)
    cwd_label.setText(cwd_label_txt)

def run(px_x: int, px_y: int, slices_z: int):
    """Run the main pipeline.

    Description

    :param 1:
    
        What that is

    :return:
    """


    #save()

    #running macro

def set_paramaters(x_pixel_input,  y_pixels_input :int,  z_slices_input :int,bytes_before_img_input :int, bytes_between_img_input:int):
    px_x=x_pixel_input
    px_y=y_pixels_input
    z_slices=z_slices_input
    bytes_before_images=bytes_before_img_input
    bytes_between_images=bytes_between_img_input
    print(px_x)

def set_controls(u16_bit_conv,u8_bit_conv, u8_bit_conv_dnzd):
    raw_to_16bit=u16_bit_conv
    raw_to_8bit=u8_bit_conv
    raw_to_8bit_dnzd=u8_bit_conv_dnzd
    print(raw_to_16bit)


#FROM UI INPUTS
if __name__ == "__main__":
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
    steps_dir_button.clicked.connect( lambda: set_controls(convert_16bit_radio.isChecked(),convert_8bit_radio.isChecked(),resize_8bit_radio))
    steps_layout.addWidget(steps_dir_button)

    # Add radio button section to main layout
    main_layout.addLayout(steps_layout)

    # Set the layout to the main window
    window.setLayout(main_layout)

    # Show the window
    window.show()

    #TODO RUN BUTTON

    # Run the application
    sys.exit(app.exec_())
