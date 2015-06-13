import math
from classes.Point import Point
from classes.Box import Box


class Grid:
    """
    Creates and manipulates grid of Boxes over the image,
    forces As Rigid As Possible image deformation
    via regularization and redraws the image
    """

    BOX_SIZE = 32
    CONTROL_WEIGHT = 100000

    iter = 0
    id = None

    def __init__(self, cw, image):

        self.visible = False

        self.cw = cw

        self._image = image
        self._points = {}
        self._boxes = []

        immask = self._image.mask

        # find borders of image
        top = self._border(immask)
        btm = self._image.height - self._border(immask[::-1])
        lft = self._border(immask.T)
        rgt = self._image.width - self._border(immask.T[::-1])

        width = rgt-lft
        height = btm-top

        box_count = (int(math.ceil(width/self.BOX_SIZE)), int(math.ceil(height/self.BOX_SIZE)))
        box_x = lft - int((box_count[0] * self.BOX_SIZE - width) / 2)
        box_y = top - int((box_count[1] * self.BOX_SIZE - height) / 2)

        # create Boxes over image
        for y in range(box_y, btm, self.BOX_SIZE):
            for x in range(box_x, rgt, self.BOX_SIZE):
                if -1 != self._border(immask[y:y+self.BOX_SIZE:1, x:x+self.BOX_SIZE:1]):
                    if x < 0 or x + self.BOX_SIZE > self._image.width \
                            or y < 0 or y + self.BOX_SIZE > self._image.height:
                        continue

                    self._boxes.append(
                        Box(
                            self.cw,
                            self._add_point(x, y),
                            self._add_point(x+self.BOX_SIZE, y),
                            self._add_point(x+self.BOX_SIZE, y+self.BOX_SIZE),
                            self._add_point(x, y+self.BOX_SIZE)
                        )
                    )

        """
        Control points setup
        key: Handle ID from ImageHelper
        item: [point ref, (x, y target coordinates), (x, y offset of grid Point from handle)]
        """
        self._controls = {}

    def _border(self, mask):
        """
        Finds the first row of the mask which contains foreground pixel.
        :return: row number in which the first foreground pixel was found, -1 if all pixels are empty
        """
        fg = 0
        stop = False
        for row in mask:
            i = 0
            for sign in row:
                if sign:
                    stop = True
                    break
                i += 1
            if stop:
                break
            fg += 1

        if not stop:
            return -1
        return fg

    def _add_point(self, x, y):
        """
        Creates new Point at given coordinate if it does not already exist
        :return: Point at given coordinates
        """
        if y in self._points:
            if x not in self._points[y]:
                self._points[y][x] = Point(x, y)
        else:
            self._points[y] = {}
            self._points[y][x] = Point(x, y)

        return self._points[y][x]

    def _reset_weights(self):
        """
        Set weight of each vertex in grid to 1.
        """
        for y in self._points:
            for x in self._points[y]:
                self._points[y][x].weight = 1

    def _update_weights(self):
        """
        Update weights of grid's vertices, respecting the structure of grid, i.e. run BFS from all control points.
        """
        self._reset_weights()

        queue = []
        for handle_id in self._controls:
            control_x = self._controls[handle_id][0].ix
            control_y = self._controls[handle_id][0].iy
            weight = self.CONTROL_WEIGHT

            queue.append((control_x, control_y, weight))

        size = self.BOX_SIZE
        d = [(-size, 0), (size, 0), (0, -size), (0, size)]

        while len(queue) != 0:
            x, y, w = queue.pop()

            if self._points[y][x].weight < w:
                continue

            self._points[y][x].weight = self._points[y][x].weight

            for dx, dy in d:
                nbr_x = x+dx
                nbr_y = y+dy
                nbr_w = w-self.BOX_SIZE**2
                if nbr_w > 1 \
                        and nbr_y in self._points and nbr_x in self._points[nbr_y]:
                    queue.append((nbr_x, nbr_y, nbr_w))

        for box in self._boxes:
            box.compute_source_centroid()

    def create_control_point(self, handle_id, x, y):
        """
        Creates control point if position is inside of grid and updates weights of grid's vertices.
        :return: boolean
        """
        for box in self._boxes:
            if box.has_point(x, y):

                control = box.get_closest_boundary(x, y)
                control.weight = self.CONTROL_WEIGHT

                self._controls[handle_id] = [control, (control.x, control.y), (control.x - x, control.y - y)]

                self._update_weights()
                return True

        return False

    def remove_control_point(self, handle_id):
        if handle_id in self._controls:
            del self._controls[handle_id]
            self._update_weights()

    def set_control_target(self, handle_id, x, y):
        """ Change target of control point if exists """
        dx, dy = self._controls[handle_id][2]
        self._controls[handle_id][1] = (x+dx, y+dy)

    def draw(self):
        """
        Visualize grid
        """
        self._image.canvas.delete("GRID")

        if self.visible:
            for box in self._boxes:
                box.draw(self._image.canvas, True)

    def regularize(self):
        """
        Regularize grid to preserve As Rigid As Possible deformation
        """
        for handle_id in self._controls:
            control = self._controls[handle_id]
            control[0].x = control[1][0]
            control[0].y = control[1][1]

        for box in self._boxes:
            box.fit()

        for y in self._points:
            for x in self._points[y]:
                self._points[y][x].average_linked()

    def project(self):
        """
        Create projection of current state
        Image data are properly updated
        """

        self.cw.clear(self._image.corig, self._image.cdata, self._image.width, self._image.height)

        for box in self._boxes:
            box.project(self._image)
