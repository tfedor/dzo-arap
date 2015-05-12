import numpy as np
import math

from classes.Point import Point


class Box():
    """ Represents one box in a grid layed over image"""

    def __init__(self, cw, b_tl, b_tr, b_br, b_bl):
        """
        :param cw: CWrapper object
        :param b_tl: top-left point of a box
        :param b_tr: top-right point of a box
        :param b_br: bottom-right point of a box
        :param b_bl: bottom-left point of a box
        """

        self._cw = cw
        self.boundary = [b_tl, b_tr, b_br, b_bl]

        # box fitted into boundaries
        self._rigid = [b_tl.copy(), b_tr.copy(), b_br.copy(), b_bl.copy()]

        self.boundary[0].link(self._rigid[0])
        self.boundary[1].link(self._rigid[1])
        self.boundary[2].link(self._rigid[2])
        self.boundary[3].link(self._rigid[3])

        # homography matrices
        self.H = None

        H_A = []
        H_B = [None]*8
        for s in self._rigid:
            H_A.append([s.ix, s.iy, 1, 0, 0, 0, None, None])
            H_A.append([0, 0, 0, s.ix, s.iy, 1, None, None])

        self.H_A = np.array(H_A)
        self.H_B = np.array(H_B)

        # centroids cache
        self._qc = Point(0, 0)  # target centroid
        self._pc = Point(0, 0)  # source centroid, same during whole object live
        self.compute_source_centroid()

    def has_point(self, x, y):
        """
        Checks whether given coordinates are inside of this box's bounding box
        :return: boolean
        """

        xs = [p.x for p in self.boundary]
        ys = [p.y for p in self.boundary]

        return min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)

    def get_closest_boundary(self, x, y):
        """ Get closest boundary Point to given position """
        min_ = -1
        closest = None
        for b in self.boundary:
            dist = abs(b.x - x) + abs(b.y - y)
            if min_ == -1 or dist < min_:
                min_ = dist
                closest = b
        return closest

    def draw(self, canvas, rigid=True):
        """
        :param rigid: whether to draw rigid box fitted into current boundaries. Default True.
        """

        if rigid:
            canvas.create_line(self._rigid[0].coor, self._rigid[1].coor, fill="blue", tag="GRID")
            canvas.create_line(self._rigid[1].coor, self._rigid[2].coor, fill="blue", tag="GRID")
            canvas.create_line(self._rigid[2].coor, self._rigid[3].coor, fill="blue", tag="GRID")
            canvas.create_line(self._rigid[3].coor, self._rigid[0].coor, fill="blue", tag="GRID")

        canvas.create_line(self.boundary[0].coor, self.boundary[1].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[1].coor, self.boundary[2].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[2].coor, self.boundary[3].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[3].coor, self.boundary[0].coor, fill="red", tag="GRID")

    def compute_source_centroid(self):
        w = self.boundary[0].weight + self.boundary[1].weight + self.boundary[2].weight + self.boundary[3].weight
        self._pc.x = (self.boundary[0].weight * self._rigid[0].ix
                      + self.boundary[1].weight * self._rigid[1].ix
                      + self.boundary[2].weight * self._rigid[2].ix
                      + self.boundary[3].weight * self._rigid[3].ix) / w
        self._pc.y = (self.boundary[0].weight * self._rigid[0].iy
                      + self.boundary[1].weight * self._rigid[1].iy
                      + self.boundary[2].weight * self._rigid[2].iy
                      + self.boundary[3].weight * self._rigid[3].iy) / w

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
        """
        Computes the best rotation and translation of the associated rigid box to minimize distance to boundaries
        """

        self.compute_target_centroid()

        rotation = [[0, 0], [0, 0]]

        for i in range(0, 4):

            p_roof_x = self._rigid[i].ix - self._pc.x
            p_roof_y = self._rigid[i].iy - self._pc.y

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
        Computes inverse homography.
        Source is initial position of the box, target is current boundary.
        """

        for i in range(0, 4):
            s = self._rigid[i]
            t = self.boundary[i]
            self.H_A[2*i][6] = -s.ix*t.x
            self.H_A[2*i][7] = -s.iy*t.x

            self.H_A[2*i+1][6] = -s.ix*t.y
            self.H_A[2*i+1][7] = -s.iy*t.y

            self.H_B[2*i] = t.x
            self.H_B[2*i+1] = t.y

        h = np.linalg.solve(self.H_A, self.H_B)
        self.H = np.linalg.inv(np.array([[h[0], h[1], h[2]],
                                         [h[3], h[4], h[5]],
                                         [h[6], h[7],   1]]))

    def project(self, image):
        """ Projects image to current boundaries """

        self._homography()

        vert = np.array([(int(round(p.x)), int(round(p.y))) for p in self.boundary])
        self._cw.project(self.H.ctypes, image.cmask, image.corig, image.cdata, image.width, image.height, vert.ctypes)

