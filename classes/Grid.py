import math
from classes.CWrapper import CWrapper
from classes.Point import Point
from classes.Box import Box


class Grid:

    iter = 0
    id = None

    def __init__(self, image):

        BOX_SIZE = 32
        self.BOX_SIZE = BOX_SIZE

        self.__image = image
        self.__points = {}
        self.__boxes = []

        imdata = self.__image.orig
        bg = imdata[0][0]

        # find borders of image
        top = self.__border(bg, imdata)
        btm = self.__image.height - self.__border(bg, imdata[::-1])
        lft = self.__border(bg, imdata.T)
        rgt = self.__image.width - self.__border(bg, imdata.T[::-1])

        width = rgt-lft
        height = btm-top

        box_count = (int(math.ceil(width/BOX_SIZE)), int(math.ceil(height/BOX_SIZE)))
        box_x = lft - int((box_count[0] * BOX_SIZE - width) / 2)
        box_y = top - int((box_count[1] * BOX_SIZE - height) / 2)

        for y in range(box_y, btm, BOX_SIZE):
            for x in range(box_x, rgt, BOX_SIZE):
                if -1 != self.__border(bg, imdata[y:y+BOX_SIZE:1, x:x+BOX_SIZE:1]):
                    self.__boxes.append(
                        Box(
                            self.__add_point(x, y),
                            self.__add_point(x+BOX_SIZE, y),
                            self.__add_point(x+BOX_SIZE, y+BOX_SIZE),
                            self.__add_point(x, y+BOX_SIZE)
                        )
                    )

        self._controls = {}

    def __border(self, empty, data):
        """
        :param empty: rgb tuple which represents empty space
        :param data: image data to go through
        :return: row number in which the first non-empty pixel was found, -1 if all pixels are empty
        """
        nonempty = 0
        stop = False
        for row in data:
            i = 0
            for rgb in row:
                if rgb[0] != empty[0] and rgb[1] != empty[1] and rgb[2] != empty[2]:
                    stop = True
                    break
                i += 1
            if stop:
                break
            nonempty += 1

        if not stop:
            return -1
        return nonempty

    def __add_point(self, x, y):
        if y in self.__points:
            if x not in self.__points[y]:
                self.__points[y][x] = Point(x, y)
        else:
            self.__points[y] = {}
            self.__points[y][x] = Point(x, y)

        return self.__points[y][x]

    def create_control_point(self, handle_id, x, y):
        for box in self.__boxes:
            if box.has_point(x, y):

                control = box.get_closest_boundary(x, y)
                control.weight = 100000

                # controls[handle_id] = (point, target_pos, handle offset)
                self._controls[handle_id] = [control, (control.x, control.y), (control.x - x, control.y - y)]

                self._set_weights(control.x, control.y, 100000)

                return True

        return False

    def remove_control_point(self, handle_id):
        if handle_id in self._controls:
            self._controls[handle_id][0].weight = 1
            del self._controls[handle_id]

    def set_control_target(self, handle_id, x, y):
        dx, dy = self._controls[handle_id][2]
        self._controls[handle_id][1] = (x+dx, y+dy)

    def draw(self):
        self.__image.canvas.delete("GRID")

        for box in self.__boxes:
            box.draw(self.__image.canvas)

    def regularize(self):
        for handle_id in self._controls:
            control = self._controls[handle_id]
            control[0].x = control[1][0]
            control[0].y = control[1][1]

        for box in self.__boxes:
            box.fit()

        for y in self.__points:
            for x in self.__points[y]:
                self.__points[y][x].average_linked()

    def project(self):
        cw = CWrapper()
        cw.clear(self.__image.cdata, self.__image.width, self.__image.height)

        for box in self.__boxes:
            box.project(self.__image)

    def _set_weights(self, control_x, control_y, weight):

        queue = []
        closed = set()

        queue.append((control_x, control_y, weight))
        closed.add((control_x, control_y))

        size = self.BOX_SIZE
        d = [(-size, 0), (size, 0), (0, -size), (0, size)]

        while len(queue) != 0:
            x, y, w = queue.pop()

            self.__points[y][x].weight = max(w, self.__points[y][x].weight)

            for dx, dy in d:
                nbr_x = x+dx
                nbr_y = y+dy
                nbr_w = w-self.BOX_SIZE**2
                if nbr_y in self.__points and nbr_x in self.__points[nbr_y] and (nbr_x, nbr_y) not in closed:
                    queue.append((nbr_x, nbr_y, nbr_w))
                    closed.add((nbr_x, nbr_y))

        for box in self.__boxes:
            box.compute_source_centroid()
