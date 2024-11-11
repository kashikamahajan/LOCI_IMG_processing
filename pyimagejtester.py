
import imagej
from scyjava import jimport

ij = imagej.init()
print(f"Image version: {ij.getversion()}")