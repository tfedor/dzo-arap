from ctypes import *
from PIL import Image
import numpy as np

# im = Image.open("assets/taz.jpg");
# c_im = np.array(im).ctypes

a = np.array([[1, 2, 3],
              [4, 5, 6]])
c_im = a.ctypes

lib = cdll.libfoo
# lib.project(c_im.data_as(ctypes.POINTER(ctypes.c_char)), 2, 3)

print(a)

project = lib.project
project(c_im.data)

print(a)

