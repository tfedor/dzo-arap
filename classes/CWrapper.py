import ctypes as c


class CWrapper:

    def __init__(self):
        self._lib = c.cdll.libproject

        self._clear = self._lib.clear
        # self._clear.argtypes = []

    def mask(self, mask, orig, width, height, tolerance):
        self._lib.compute_mask(mask.data, orig.data, width, height, tolerance)

    def clear(self, data, width, height):
        self._lib.clear(data.data_as(c.POINTER(c.c_char)), width, height)

    def project(self, homography, mask, orig, data, width, height, corners):

        self._lib.project(
            homography.data,
            mask.data,
            orig.data,
            data.data,
            width,
            height,
            corners.data
        )
