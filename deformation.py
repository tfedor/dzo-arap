from PIL import Image, ImageTk, ImageDraw, ImageColor
import math
import tkinter as tk

NBR_SIZE = 16
NBR_OFFSET = NBR_SIZE/2

SEARCH_SIZE = 48
SEARCH_OFFSET = SEARCH_SIZE/2


class ImageWidget():

    def __init__(self, parent, path):

        self.image = None
        self.data = []

        self.update(Image.open(path))

        photo = ImageTk.PhotoImage(self.image)
        self.label = tk.Label(parent, image=photo)
        self.label.image = photo
        self.label.pack(side=tk.LEFT)

    def bind(self, event, callback):
        self.label.bind(event, callback)

    def update(self, image):
        self.image = image
        self.data = list(self.image.getdata())

    def redraw(self):
        photo = ImageTk.PhotoImage(self.image)
        self.label.configure(image=photo)
        self.label.image = photo

    def clear_overlay(self):
        self.image.putdata(self.data)

    def px(self, x, y):
        return self.data[y * self.image.size[0] + x]

    def draw_box(self, x, y, offset, color):

        draw = ImageDraw.Draw(self.image)
        draw.rectangle([(x-offset, y-offset),
                        (x+offset, y+offset)], outline=color)

    def draw_line(self, start, end, color=(255, 0, 255), width=1):
        draw = ImageDraw.Draw(self.image)
        draw.line([start, end], fill=color, width=width)


class Point():
    """ Embedding lattice point with defined position, neighbourhood and search area """

    def __init__(self, x, y):
        self.pos = [x, y]
        #print(self.pos)

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, value):
        self.pos[0] = value

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, value):
        self.pos[1] = value

    def push(self):

        min = None
        minT = None

        for tx in range(-24, 24+1):
            for ty in range(-24, 24+1):
                sum = 0
                for px in range(self.x-8, self.x+8+1):
                    for py in range(self.y-8, self.y+8+1):
                        srcPixel = widget_edit.px(px-tx, py-ty)
                        tgtPixel = widget_target.px(px, py)

                        sum += math.sqrt( (srcPixel[0]-tgtPixel[0])**2 + (srcPixel[1]-tgtPixel[1])**2 + (srcPixel[2]-tgtPixel[2])**2 )

                        if min is not None and sum >= min:
                            break

                    if min is not None and sum >= min:
                        break

                if min is None or sum < min:
                    min = sum
                    minT = (tx, ty)

        return minT


def create_point(e):
    lattice = []
    lattice.append(Point(e.x, e.y))
    lattice.append(Point(e.x - NBR_SIZE, e.y))
    lattice.append(Point(e.x - NBR_SIZE, e.y + NBR_SIZE))
    lattice.append(Point(e.x, e.y + NBR_SIZE))

    after = []

    widget_edit.clear_overlay()
    widget_target.clear_overlay()

    widget_edit.draw_box(e.x-NBR_OFFSET, e.y+NBR_OFFSET, NBR_OFFSET, (255, 0, 0)) # lattice

    ## push
    for point in lattice:
        #widget_edit.draw_box(point.x, point.y, 24, (255, 0, 0))
        widget_edit.draw_box(point.x, point.y, 8, (0, 0, 255))

        t = point.push()
        print(t)

        after.append(Point(point.x+t[0], point.y+t[1]))

        #widget_target.draw_line((point.x, point.y), (point.x+t[0], point.y+t[1]), color=(255, 0, 255))  # change line
        #widget_target.draw_box(point.x, point.y, 8, (0, 255, 0))
        #widget_target.draw_box(point.x, point.y, 24, (0, 255, 0))
        #widget_target.draw_box(point.x+t[0], point.y+t[1], 24, (255, 0, 0))
        widget_target.draw_box(point.x+t[0], point.y+t[1], 8, (0, 255, 0))  # new nbr

    for i in range(0, 4):
        widget_target.draw_line((after[i].x, after[i].y), (after[(i+1) % 4].x, after[(i+1) % 4].y), color=(255, 0, 0), width=2)

    ## regularize
    p_c = Point((lattice[0].x + lattice[1].x + lattice[2].x + lattice[3].x) / 4,
                (lattice[0].y + lattice[1].y + lattice[2].y + lattice[3].y) / 4)
    q_c = Point((after[0].x + after[1].x + after[2].x + after[3].x) / 4,
                (after[0].y + after[1].y + after[2].y + after[3].y) / 4)

    widget_edit.draw_box(p_c.x, p_c.y, 1, color=(255, 255, 0))
    widget_target.draw_box(q_c.x, q_c.y, 1, color=(255, 255, 0))

    """
    Rstar = [[0, 0], [0, 0]]
    mi_1 = 0
    mi_2 = 0
    for i, point in enumerate(lattice):
        p_roof = (point.x - p_c.x, point.y - p_c.y)
        q_roof = (after[i].x - q_c.x, after[i].y - q_c.y)

        Rstar[0][0] += (p_roof[0]*q_roof[0] + p_roof[1]*q_roof[1])
        Rstar[0][1] += (p_roof[0]*q_roof[1] - p_roof[1]*q_roof[0])
        Rstar[1][0] += (p_roof[1]*q_roof[0] - p_roof[0]*q_roof[1])
        Rstar[1][1] += (p_roof[1]*q_roof[1] + p_roof[0]*q_roof[0])

        mi_1 += q_roof[0]*p_roof[0] + q_roof[1]*p_roof[1]
        mi_2 += q_roof[0]*p_roof[1] - q_roof[1]*p_roof[0]

    mi = math.sqrt(mi_1**2 + mi_2**2)

    print(Rstar)
    Rstar[0][0] /= mi
    Rstar[0][1] /= mi
    Rstar[1][0] /= mi
    Rstar[1][1] /= mi

    Tstar = (p_c.x - (Rstar[0][0]*q_c.x + Rstar[1][0]*q_c.y),
             p_c.y - (Rstar[1][0]*q_c.x + Rstar[1][1]*q_c.y))
    print(Tstar)

    final = []
    for point in lattice:
        final.append(Point(point.x+Tstar[0], point.y+Tstar[1]))

    for i in range(0, 4):
        print(lattice[i].x, lattice[i].y, final[i].x, final[i].y)
        widget_target.draw_line((final[i].x, final[i].y), (final[(i+1) % 4].x, final[(i+1) % 4].y), color=(255, 0, 255), width=3)
    """

    widget_edit.redraw()
    widget_target.redraw()


# load and open images
window = tk.Tk()

widget_edit = ImageWidget(window, "assets/taz.jpg")
widget_edit.bind("<Button-1>", create_point)

widget_target = ImageWidget(window, "assets/taz_small.jpg")

# prepare editing image
box = None

# pack
frame = tk.Frame(window)
frame.pack()

#

# window.protocol("WM_DELETE_WINDOW", windowClose)
window.mainloop()
