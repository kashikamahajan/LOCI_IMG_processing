import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QFileDialog

# Create a function to handle button click
def get_directory():
    working_dir = QFileDialog.getExistingDirectory(None, 'Select Directory')
    cwd_label_txt = "Current Directory: " + str(working_dir)
    cwd_label.setText(cwd_label_txt)

# Initialize the application
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle("Simple PyQt App")
window.resize(600, 400)

# Create a label and a button
cwd_label_txt = "Current Directory: " + os.getcwd()
cwd_label = QLabel(cwd_label_txt, window)
button = QPushButton("Select Directory", window)

# Connect button click to the function
button.clicked.connect(get_directory)

# Manually set the position of the button
button.move(100, 20)

# Show the window
window.show()

# Run the application
sys.exit(app.exec_())
