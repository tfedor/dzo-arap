class Point():
    """ Embedding lattice point with defined position, neighbourhood and search area """

    w = 1

    def __init__(self, x, y, w=1):
        self.pos = [x, y]
        self._init = (x, y)  # intial state of point, doesn't need to be mutable
        self.linked = []
        self._link_cnt = 0
        self.w = w

        self.init = [x, y]

    def reset(self):
        self.pos[0] = self.init[0]
        self.pos[1] = self.init[1]

    @property
    def weight(self):
        return self.w

    @weight.setter
    def weight(self, value):
        self.w = value

    @property
    def x(self):
        return self.pos[0]

    @property
    def ix(self):
        return self._init[0]

    @x.setter
    def x(self, value):
        self.pos[0] = value

    @property
    def y(self):
        return self.pos[1]

    @property
    def iy(self):
        return self._init[1]

    @y.setter
    def y(self, value):
        self.pos[1] = value

    @property
    def coor(self):
        return self.pos[0], self.pos[1]

    def copy(self):
        return Point(self.x, self.y, self.weight)

    def sub(self, point):
        self.x -= point.x
        self.y -= point.y
        return self

    def rotate(self, rotation):
        x = rotation[0][0] * self.x + rotation[1][0] * self.y
        y = rotation[0][1] * self.x + rotation[1][1] * self.y
        self.x = x
        self.y = y
        return self

    def translate(self, translation):
        self.x += translation.x
        self.y += translation.y
        return self

    def link(self, other):
        self.linked.append(other)
        self._link_cnt += 1

    def average_linked(self):
        x = 0
        y = 0
        for point in self.linked:
            x += point.x
            y += point.y
        x /= self._link_cnt
        y /= self._link_cnt

        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

