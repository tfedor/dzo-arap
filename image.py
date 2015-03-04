from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

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

        plt.ylim([0, max(hist)])
        for i, h in enumerate(hist):
            self.rects[i].set_height(h)

        self.canvas.draw()


class Callback():

    def __init__(self, orig, edit, widget, hist):
        self.im_orig = orig
        self.im_edit = edit
        self.widget = widget
        self.hist = hist

    def __call__(self, value):
        data = self.op(self.im_orig.getdata(), float(value))

        self.im_edit.putdata(data)
        self.widget.update(self.im_edit)
        self.hist.update(self.im_edit)

    def op(self, pixels, param=None):
        return pixels


class Negative(Callback):

    def op(self, pixels, param=None):
        newdata = []
        for pixel in pixels:
            newdata.append(255-pixel)
        return newdata


class Threshold(Callback):

    def op(self, pixels, threshold):
        newdata = []
        for pixel in pixels:
            val = 0 if pixel < threshold else 255
            newdata.append(val)
        return newdata


class Contrast(Callback):

    def op(self, pixels, c):
        newdata = []
        for pixel in pixels:
            val = ((pixel/256.0)*c)*256
            newdata.append(val)
        return newdata


class Gamma(Callback):

    def op(self, pixels, g):
        table = range(0,256)
        newdata = [0]*len(pixels)
        i = 0
        for pixel in pixels:
            val = ((pixel/256.0)**g)*256
            newdata[i] = val
            i += 1
        return newdata

    def op2(self, pixels, g):
        newdata = [0]*len(pixels)
        i = 0
        for pixel in pixels:
            val = ((pixel/256.0)**g)*256
            newdata[i] = val
            i += 1
        return newdata


def windowClose():
    print("close")
    window.destroy()

path = "lena.jpg"

im_orig = Image.open(path)
im_orig.load()
data = list(im_orig.getdata())

im_edit = Image.new(im_orig.mode, im_orig.size)

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
    call = cb[value]
    s.configure(command=call)
    call(0)

    if value == "Threshold":
        s.configure(from_=0, to=255)
    elif value == "Negative":
        pass
    else:
        s.configure(from_=0, to=10)


button = tk.Button(frame, text="OK", command=ok)
button.pack(side=tk.RIGHT)

#

window.protocol("WM_DELETE_WINDOW", windowClose)
window.mainloop()
