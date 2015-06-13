import tkinter as tk
from datetime import datetime

from classes.ImageHelper import ImageHelper
from classes.Grid import Grid
from classes.CWrapper import CWrapper


class Application:

    def __init__(self, path):
        self._cw = CWrapper()

        self._window = tk.Tk()

        self._grid = None
        self._image = None
        self.load_image(path)

        self._canvas = tk.Canvas(self._window, width=self._image.width, height=self._image.height)
        self._canvas.pack()

        self._image.canvas = self._canvas

        self._active_handle = -1
        self._loop = None
        self._t_last = 0

    def load_image(self, path):
        self._image = ImageHelper(self._cw, path)

    def bind(self, event, fn):
        self._canvas.bind(event, fn)

    def run(self):
        self._grid = Grid(self._cw, self._image)
        self._image.draw()
        self._grid.draw()

        self._run_once()

        self._window.mainloop()

    def _run_once(self):

        self._grid.regularize()

        dt = datetime.now()
        delta = dt.timestamp()-self._t_last
        if 0 < delta > 0.03:  # 0.03 - 30 FPS

            # dt = datetime.now()
            # t1 = dt.timestamp()

            self._grid.project()

            #dt = datetime.now()
            # print(dt.timestamp()-t1)

            self._image.draw()
            self._grid.draw()

            dt = datetime.now()
            self._t_last = dt.timestamp()

        self._loop = self._window.after(1, self._run_once)

    def select_handle(self, e):
        handle_id = self._image.select_handle(e.x, e.y)

        if handle_id == -1:
            handle_id = self._image.create_handle(e.x, e.y)
            if handle_id != -1:
                if not self._grid.create_control_point(handle_id, e.x, e.y):
                    self._image.remove_handle(handle_id)
                    return False
            else:
                return False

        self._active_handle = handle_id
        return True

    def deselect_handle(self, e):
        self._active_handle = -1

    def remove_handle(self, e):
        handle_id = self._image.select_handle(e.x, e.y)
        if handle_id != -1:
            self._grid.remove_control_point(handle_id)
            self._image.remove_handle(handle_id)

    def move_handle(self, e):
        if self._active_handle != -1:
            self._image.move_handle(self._active_handle, e.x, e.y)
            self._grid.set_control_target(self._active_handle, e.x, e.y)
