import numpy as np
from PIL import Image, ImageTk


class ImageHelper:
    """
    Manipulates directly with image.
    Ensures it's loading, updating and redrawing as well as provides info about loaded image.
    """

    """ radius of visual representation of control point """
    HANDLE_RADIUS = 5

    def __init__(self, cw, path):
        self.cw = cw
        self._canvas = None

        self._im_obj = Image.open(path)
        self._tk_obj = ImageTk.PhotoImage(self._im_obj)  # keeping reference for image to load

        self._size = self._im_obj.size
        self._pos = (self.width/2, self.height/2)

        self._orig = np.array(self._im_obj)  # original data of the image immediately after load
        self._data = np.array(self._im_obj)  # current data of the image to draw

        self._mask = None
        self._compute_mask()

        self._handles = set()

    @property
    def canvas(self):
        return self._canvas

    @canvas.setter
    def canvas(self, canvas):
        self._canvas = canvas

    @property
    def width(self):
        return self._size[0]

    @property
    def height(self):
        return self._size[1]

    @property
    def mask(self):
        return self._mask

    @property
    def cmask(self):
        """
        :return: Object for communicating with C interface for image mask
        """
        return self._mask.ctypes

    @property
    def cdata(self):
        """
        :return: Object for communicating with C interface for current image data
        """
        return self._data.ctypes

    @property
    def corig(self):
        """
        :return: Object for communicating with C interface for data of original image
        """
        return self._orig.ctypes

    def _compute_mask(self):
        """ Compute mask of image - foreground is True, background is False """
        self._mask = np.full((self.height, self.width), True, dtype=np.bool)
        self.cw.mask(self.cmask, self.corig, self.width, self.height, 10)

    def _update(self):
        """ Create new image from current data """
        self._im_obj = Image.fromarray(self._data)  # putdata(self._data)
        self._tk_obj = ImageTk.PhotoImage(self._im_obj)  # need to keep reference for image to load

    def draw(self):
        """ Redraw image from associated data """
        self._update()

        self._canvas.delete("IMAGE")
        self._canvas.create_image(self._pos, image=self._tk_obj, tag="IMAGE")

        for h in self._handles:
            self._canvas.tag_raise(h)

        return True

    def create_handle(self, x, y):
        """
        Creates handle at given position if it doesn't exist yet
        :return: Handle ID or -1 if creation failed due to overlap with existing one
        """
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)

        overlap = self._canvas.find_overlapping(bbox[0], bbox[1], bbox[2], bbox[3])
        for obj_id in overlap:
            if obj_id in self._handles:
                return -1

        handle_id = self._canvas.create_oval(bbox, fill="blue", outline="blue", tag="HANDLE")
        self._handles.add(handle_id)
        return handle_id

    def select_handle(self, x, y):
        """
        Checks if there is handle at given position
        :return: Handle ID if handle at position exists, -1 otherwise
        """
        overlap = self._canvas.find_overlapping(x, y, x, y)
        for obj_id in overlap:
            if obj_id in self._handles:
                return obj_id

        return -1

    def move_handle(self, handle_id, x, y):
        """ Change position of given handle """
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)
        self._canvas.coords(handle_id, bbox)

    def remove_handle(self, handle_id):
        """ Removes handle """
        self._canvas.delete(handle_id)
        self._handles.remove(handle_id)
