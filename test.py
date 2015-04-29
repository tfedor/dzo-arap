from ctypes import *

libc = cdll.msvcrt

printf = libc.printf
printf(b"Hello, \n%s", b"World!")