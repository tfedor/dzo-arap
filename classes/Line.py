
class Line:
    """
    Bresenham's line
    http://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    """

    def __init__(self):
        self.stack = dict()
        self.res = []

    def addp(self, p1, p2):
        self.add(int(round(p1.x)), int(round(p1.y)), int(round(p2.x)), int(round(p2.y)))

    def add(self, x0, y0, x1, y1):

        self.res = []

        dx = abs(x1-x0)
        dy = abs(y1-y0)

        if dx > dy:
            for x, y in self.points(x0, y0, x1, y1):
                self.res.append((x, y))

                if y not in self.stack:
                    self.stack[y] = (x, x)
                else:
                    self.stack[y] = (min(self.stack[y][0], x), max(self.stack[y][1], x))
        else:
            for y, x in self.points(y0, x0, y1, x1):
                self.res.append((x, y))

                if y not in self.stack:
                    self.stack[y] = (x, x)
                else:
                    self.stack[y] = (min(self.stack[y][0], x), max(self.stack[y][1], x))

    def points(self, x0, y0, x1, y1):

        dx = abs(x1-x0)
        dy = abs(y1-y0)

        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0

        if y1 < y0:
            x0, y0, x1, y1 = x0, -y0, x1, -y1

        D = 2*dy - dx

        yield abs(x0), abs(y0)

        y = y0
        for x in range(x0+1, x1):
            D += 2*dy
            if D > 0:
                y += 1
                D -= 2*dx

            yield abs(x), abs(y)
