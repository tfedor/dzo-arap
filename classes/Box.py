import numpy as np
import math

from classes.Line import Line
from classes.CWrapper import CWrapper
from classes.Point import Point


class Box():

    def __init__(self, b_tl, b_tr, b_br, b_bl):
        # initial position of a box, used for modifying image
        self._initial = [b_tl.copy(), b_tr.copy(), b_br.copy(), b_bl.copy()]

        self.boundary = [b_tl, b_tr, b_br, b_bl]

        # box fitted into boundaries
        self._rigid = [b_tl.copy(), b_tr.copy(), b_br.copy(), b_bl.copy()]

        self.boundary[0].link(self._rigid[0])
        self.boundary[1].link(self._rigid[1])
        self.boundary[2].link(self._rigid[2])
        self.boundary[3].link(self._rigid[3])

        self._rasterized = []
        self.rasterize()

        self.H = None

        H_A = []
        H_B = [None]*8
        for s in self._initial:
            H_A.append([s.x, s.y, 1, 0, 0, 0, None, None])
            H_A.append([0, 0, 0, s.x, s.y, 1, None, None])

        self.H_A = np.array(H_A)
        self.H_B = np.array(H_B)

        self._r_min = 0
        self._r_max = 0
        self._r_flat = np.array([])

        #
        self._pc = Point(0, 0)
        self.compute_source_centroid()

        self._qc = Point(0, 0)

    def rasterize(self):

        lines = Line()
        lines.addp(self.boundary[0], self.boundary[1])
        lines.addp(self.boundary[1], self.boundary[2])
        lines.addp(self.boundary[2], self.boundary[3])
        lines.addp(self.boundary[3], self.boundary[0])
        self._rasterized = lines.stack

        self._r_min = min(self._rasterized.keys())
        self._r_max = max(self._rasterized.keys())
        self._r_flat = np.array([c for key in range(self._r_min, self._r_max) for c in self._rasterized[key]]).astype(int)

    def has_point(self, x, y):
        if y in self._rasterized:
            left, right = self._rasterized[y]
            return left <= x <= right
        return False

    def draw(self, canvas):

        # canvas.create_line(self._initial[0].coor, self._initial[1].coor, fill="yellow", tag="GRID")
        # canvas.create_line(self._initial[1].coor, self._initial[2].coor, fill="yellow", tag="GRID")
        # canvas.create_line(self._initial[2].coor, self._initial[3].coor, fill="yellow", tag="GRID")
        # canvas.create_line(self._initial[3].coor, self._initial[0].coor, fill="yellow", tag="GRID")

        canvas.create_line(self._rigid[0].coor, self._rigid[1].coor, fill="blue", tag="GRID")
        canvas.create_line(self._rigid[1].coor, self._rigid[2].coor, fill="blue", tag="GRID")
        canvas.create_line(self._rigid[2].coor, self._rigid[3].coor, fill="blue", tag="GRID")
        canvas.create_line(self._rigid[3].coor, self._rigid[0].coor, fill="blue", tag="GRID")

        canvas.create_line(self.boundary[0].coor, self.boundary[1].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[1].coor, self.boundary[2].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[2].coor, self.boundary[3].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[3].coor, self.boundary[0].coor, fill="red", tag="GRID")

    def get_closest_boundary(self, x, y):
        min_ = -1
        closest = None
        for b in self.boundary:
            dist = abs(b.x - x) + abs(b.y - y)
            if min_ == -1 or dist < min_:
                min_ = dist
                closest = b
        return closest

    def compute_source_centroid(self):
        w = self.boundary[0].weight + self.boundary[1].weight + self.boundary[2].weight + self.boundary[3].weight
        self._pc.x = (self.boundary[0].weight * self._initial[0].x
                      + self.boundary[1].weight * self._initial[1].x
                      + self.boundary[2].weight * self._initial[2].x
                      + self.boundary[3].weight * self._initial[3].x) / w
        self._pc.y = (self.boundary[0].weight * self._initial[0].y
                      + self.boundary[1].weight * self._initial[1].y
                      + self.boundary[2].weight * self._initial[2].y
                      + self.boundary[3].weight * self._initial[3].y) / w

    def compute_target_centroid(self):
        w = self.boundary[0].weight + self.boundary[1].weight + self.boundary[2].weight + self.boundary[3].weight
        self._qc.x = (self.boundary[0].weight * self.boundary[0].x
                      + self.boundary[1].weight * self.boundary[1].x
                      + self.boundary[2].weight * self.boundary[2].x
                      + self.boundary[3].weight * self.boundary[3].x) / w
        self._qc.y = (self.boundary[0].weight * self.boundary[0].y
                      + self.boundary[1].weight * self.boundary[1].y
                      + self.boundary[2].weight * self.boundary[2].y
                      + self.boundary[3].weight * self.boundary[3].y) / w

    def fit(self):

        self.compute_target_centroid()

        rotation = [[0, 0], [0, 0]]

        for i in range(0, 4):

            p_roof_x = self._initial[i].x - self._pc.x
            p_roof_y = self._initial[i].y - self._pc.y

            q_roof_x = self.boundary[i].x - self._qc.x
            q_roof_y = self.boundary[i].y - self._qc.y

            weight = self.boundary[i].weight
            pq_x = p_roof_x * q_roof_x
            pq_y = p_roof_y * q_roof_y
            pq_xy = p_roof_x * q_roof_y
            pq_yx = p_roof_y * q_roof_x
            rotation[0][0] += weight * (pq_x + pq_y)
            rotation[0][1] += weight * (pq_xy - pq_yx)
            rotation[1][0] += weight * (pq_yx - pq_xy)

            # mi_1 += self.boundary[i].weight * (pq_x + pq_y)
            # mi_2 += self.boundary[i].weight * (pq_yx - pq_xy)

            self._rigid[i].x = p_roof_x
            self._rigid[i].y = p_roof_y

        mi = 1 / math.sqrt(rotation[0][0]**2 + rotation[1][0]**2)

        rotation[0][0] *= mi
        rotation[0][1] *= mi
        rotation[1][0] *= mi
        rotation[1][1] = rotation[0][0]

        for i, point in enumerate(self._rigid):
            self._rigid[i].rotate(rotation).translate(self._qc)

    def _homography(self):

        """
        H_A = []
        H_B = []

        i = 0
        for s in self._initial:
            t = self.boundary[i]

            H_A.append([t.x, t.y, 1, 0, 0, 0, -t.x*s.x, -t.y*s.x])
            H_A.append([0, 0, 0, t.x, t.y, 1, -t.x*s.y, -t.y*s.y])

            H_B.append(t.x)
            H_B.append(t.y)

            i += 1

        self.H_A = np.array(H_A)
        self.H_B = np.array(H_B)

        h = np.linalg.solve(self.H_A, self.H_B)
        self.H = np.array([[h[0], h[1], h[2]],
                                         [h[3], h[4], h[5]],
                                         [h[6], h[7],   1]])


        """
        for i in range(0, 4):
            s = self._initial[i]
            t = self.boundary[i]
            self.H_A[2*i][6] = -s.x*t.x
            self.H_A[2*i][7] = -s.y*t.x

            self.H_A[2*i+1][6] = -s.x*t.y
            self.H_A[2*i+1][7] = -s.y*t.y

            self.H_B[2*i] = t.x
            self.H_B[2*i+1] = t.y


        h = np.linalg.solve(self.H_A, self.H_B)
        self.H = np.linalg.inv(np.array([[h[0], h[1], h[2]],
                                         [h[3], h[4], h[5]],
                                         [h[6], h[7],   1]]))


    def project(self, image):

        self._homography()

        vert = np.array([(int(round(p.x)), int(round(p.y))) for p in self.boundary])

        cw = CWrapper()
        cw.project(self.H.ctypes, image.corig, image.cdata, image.width, image.height, vert.ctypes)

