This was a semestral project for a Digital Image Processing class at CTU, in summer semester 2014/2015.

The goal was to implement as-rigid-as-possible real-time image deformation based on following papers:
* http://dcgi.felk.cvut.cz/home/sykorad/deform.html
* http://dl.acm.org/citation.cfm?id=1141920

In reports folder of this repository are included presentation and final report, both written in Slovak but including images of achieved results.

#### Implementation
Application was implemented in Python 3.4 64bit with computationally extensive parts written in C. Python libraries used were: numpy, Pillow and TkInter.

For compilation of the library there's a very very minimal makefile added. Application wasn't tested on anything else but Windows 7 64bit.

For starting application use main.py, in which there's a hardcoded path to image.

For adding and moving control point use left mouse button, for removing use right mouse button.

#### Examples of results
![Calvin initial](https://raw.githubusercontent.com/tfedor/dzo-arap/master/reports/presentation/pic/results/calvin1.png)
![Calvin deformed](https://raw.githubusercontent.com/tfedor/dzo-arap/master/reports/presentation/pic/results/calvin2.png)

![Calvin & Hobbes initial](https://raw.githubusercontent.com/tfedor/dzo-arap/master/reports/presentation/pic/results/calvin-hobbes1.png)
![Calvin & Hobbes deformed](https://raw.githubusercontent.com/tfedor/dzo-arap/master/reports/presentation/pic/results/calvin-hobbes2.png)
