from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ImageWidget():

    def __init__(self, parent, image):
        photo = ImageTk.PhotoImage(image)
        self.label = tk.Label(parent, image=photo)
        self.label.image = photo
        self.label.pack(side=tk.LEFT)

    def update(self, image):
        photo = ImageTk.PhotoImage(image)
        self.label.configure(image=photo)
        self.label.image = photo


class Histogram():

    def __init__(self, parent, image, color):
        fig = plt.figure(facecolor="white")

        fig.add_subplot(111)
        fig.tight_layout(pad=0)
        plt.axis('off')
        plt.autoscale(enable=True)

        self.rects = plt.bar(range(0, 256), image.histogram(), color=color, edgecolor=color)

        self.canvas = FigureCanvasTkAgg(fig, master=parent)
        self.canvas.show()
        self.canvas.get_tk_widget().config(width=500, height=200, highlightthicknes=0, bd=0)
        self.canvas.get_tk_widget().pack()

    def update(self, image):
        hist = image.histogram()

        i = 0
        plt.ylim([0, max(hist)])
        for h in hist:
            self.rects[i].set_height(h)
            i += 1

        self.canvas.draw()


class Callback():

    def __init__(self, orig, edit, widget, hist):
        self.im_orig = orig
        self.im_edit = edit
        self.widget = widget
        self.hist = hist

    def __call__(self, value):
        self.im_edit = self.im_orig.point(lambda pixel: self.op(pixel, float(value)), self.im_orig.mode)

        self.widget.update(self.im_edit)
        self.hist.update(self.im_edit)

    def op(self, pixel, param=None):
        return pixel


class Negative(Callback):
    def op(self, pixel, param=None):
        return 255-pixel


class Threshold(Callback):
    def op(self, pixel, threshold):
        return 0 if pixel < threshold else 255


class Contrast(Callback):
    def op(self, pixel, c):
        return int(((pixel/256.0)*c)*256)


class Gamma(Callback):
    def op(self, pixel, g):
        return int(((pixel/256.0)**g)*256)

path = "lena.jpg"

im_orig = Image.open(path)
data = list(im_orig.getdata())

im_edit = Image.new(im_orig.mode, im_orig.size)
im_edit.putdata(data)

window = tk.Tk()

widget_orig = ImageWidget(window, im_orig)
widget_edit = ImageWidget(window, im_edit)

hist_orig = Histogram(window, im_orig, "blue")
hist_edit = Histogram(window, im_edit, "red")

cb = dict()
cb["Negative"] = Negative(im_orig, im_edit, widget_edit, hist_edit)
cb["Threshold"] = Threshold(im_orig, im_edit, widget_edit, hist_edit)
cb["Contrast"] = Contrast(im_orig, im_edit, widget_edit, hist_edit)
cb["Gamma"] = Gamma(im_orig, im_edit, widget_edit, hist_edit)

s = tk.Scale(window, from_=0, to=10, resolution=0.01, orient=tk.HORIZONTAL, length=400, command=cb["Gamma"])
s.set(1)
s.pack()

#

frame = tk.Frame(window)
frame.pack()
variable = tk.StringVar(frame)
variable.set("Gamma") # default value

w = tk.OptionMenu(frame, variable, "Negative", "Threshold", "Contrast", "Gamma")
w.pack(side=tk.LEFT)


def ok():
    value = variable.get()

    if value == "Threshold":
        s.configure(from_=0, to=255)
        s.set(128)
    elif value == "Negative":
        s.configure(from_=0, to=0)
        s.set(0)
        pass
    else:
        s.configure(from_=0, to=10)
        s.set(1)

    call = cb[value]
    s.configure(command=call)
    call(0)


button = tk.Button(frame, text="OK", command=ok)
button.pack(side=tk.RIGHT)

#

def windowClose():
    window.destroy()

# window.protocol("WM_DELETE_WINDOW", windowClose)
window.mainloop()
