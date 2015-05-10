import tkinter as tk
from datetime import datetime

from classes.ImageHelper import ImageHelper
from classes.Grid import Grid


class Application:

    def __init__(self, width, height):
        self.window = tk.Tk()

        self.width = width
        self.height = height

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        self.image = None
        self.grid = None

        self._active_handle = -1

        self._loop = None

        self.__run = False
        self._t_last = 0

    def load_image(self, path):

        self.image = ImageHelper(self.canvas, (self.width/2, self.height/2), path)
        self.image.draw()

    def bind(self, event, fn):
        self.canvas.bind(event, fn)

    def run(self):
        self.grid = Grid(self.image)
        self.image.draw()
        self.grid.draw()

        self.run_once()

        self.window.mainloop()

    def run_once(self):

        self.grid.regularize()

        dt = datetime.now()
        delta = dt.timestamp()-self._t_last
        if 0 < delta > 0.03:  # 0.03 - 30 FPS

            dt = datetime.now()
            t1 = dt.timestamp()

            self.grid.project()

            dt = datetime.now()
            print(dt.timestamp()-t1)

            self.image.draw()
            self.grid.draw()

            dt = datetime.now()
            self._t_last = dt.timestamp()

        self._loop = self.window.after(1, self.run_once)

    def select_handle(self, e):
        handle_id = self.image.select_handle(e.x, e.y)

        if handle_id == -1:
            handle_id = self.image.create_handle(e.x, e.y)
            if handle_id != -1:
                if not self.grid.create_control_point(handle_id, e.x, e.y):
                    self.image.remove_handle(e.x, e.y)
                    return False
            else:
                return False

        self._active_handle = handle_id
        return True

    def deselect_handle(self, e):
        self._active_handle = -1

    def remove_handle(self, e):
        handle_id = self.image.select_handle(e.x, e.y)
        if handle_id != -1:
            self.grid.remove_control_point(handle_id)
            self.image.remove_handle(handle_id)

    def move_handle(self, e):
        if self._active_handle != -1:
            self.image.move_handle(self._active_handle, e.x, e.y)
            self.grid.set_control_target(self._active_handle, e.x, e.y)
