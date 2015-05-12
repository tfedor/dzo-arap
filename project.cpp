#include <cstdio>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <map>
#include <bitset>

#define R (0)
#define G (1)
#define B (2)

extern "C" void clear(char * data, int width, int height) {

    for (int i=0; i<width*height*3; i++) {
        data[i] = 255;
    }

}

void dot(double * homography, float x, float y, float &rx, float &ry) {
    double rw;

    rx = homography[0]*x + homography[1]*y + homography[2];
    ry = homography[3]*x + homography[4]*y + homography[5];
    rw = homography[6]*x + homography[7]*y + homography[8];

    rx /= rw;
    ry /= rw;
}

//
void store(std::map<int,int> &left, std::map<int,int> &right, int x, int y) {
    if (left.count(y) > 0) {
        if (x < left[y]) {
            left[y] = x;
        } else if (right[y] < x) {
            right[y] = x;
        }
    } else {
        left[y] = x;
        right[y] = x;
    }
}
void points(std::map<int, int> &left, std::map<int,int> &right, bool swap, int x0, int y0, int x1, int y1) {

    if (swap) {
        std::swap(x0, y0);
        std::swap(x1, y1);
    }

    int dx = abs(x1-x0);
    int dy = abs(y1-y0);

    if (x0 > x1) {
        std::swap(x0, x1);
        std::swap(y0, y1);
    }

    if (y1 < y0) {
        y0 = -y0;
        y1 = -y1;
    }

    int D = 2*dy - dx;

    // add
    if (swap) {
        store(left, right, abs(y0), abs(x0));
    } else {
        store(left, right, abs(x0), abs(y0));
    }

    int y = y0;
    for (int x=x0+1; x<x1; x++) {
        D += 2*dy;
        if (D > 0) {
            y += 1;
            D -= 2*dx;
        }

        // add
        if (swap) {
            store(left, right, abs(y), abs(x));
        } else {
            store(left, right, abs(x), abs(y));
        }
    }
}
extern "C" void rasterize(int * corners, std::map<int,int> &left, std::map<int,int> &right) {

    for (int i=0; i<4; i++) {
        int x0 = corners[2*i];
        int y0 = corners[2*i + 1];
        int x1 = corners[(2*i+ 2) % 8];
        int y1 = corners[(2*i+ 3) % 8];

        int dx = abs(x1-x0);
        int dy = abs(y1-y0);

        points(left, right, (dx <= dy), x0, y0, x1, y1);
    }
}

//
extern "C" void project(double * homography, char * orig, char * data, int width, int height, int * corners) {

    std::map<int,int> left;
    std::map<int,int> right;
    rasterize(corners, left, right);

    int max_index = height*width*3;

    std::map<int,int>::iterator it;

    for (it = left.begin(); it != left.end(); ++it) {
        int y = it->first;
        int x_left = it->second;
        int x_right = right[y];

        for (int x=x_left; x<=x_right; x++) {

            float rx, ry;
            dot(homography, (float)x, (float)y, rx, ry);

            int data_index = (y*width + x)*3;

            //
            int lft = floor(rx);
            int rgt = lft+1;

            int top = floor(ry);
            int btm = top+1;

            if (lft >= 0 && rgt < width && top >= 0 && btm < height) {
                float coefX = rx-(float)lft;
                float coefY = ry-(float)top;

                //std::cout << ry << " " << top << "=" << coefY << std::endl;
                //std::cout << coefX << " " << coefY << std::endl;

                float tl = (1.f-coefX)*(1.f-coefY);
                float tr = coefX*(1.f-coefY);
                float bl = (1.f-coefX)*coefY;
                float br = coefX*coefY;

                for (int c=0; c<3; c++) {
                    float clr = tl*((int)round(orig[(top*width + lft)*3 + c])&255)
                              + tr*((int)round(orig[(top*width + rgt)*3 + c])&255)
                              + bl*((int)round(orig[(btm*width + lft)*3 + c])&255)
                              + br*((int)round(orig[(btm*width + rgt)*3 + c])&255);
                    data[data_index + c] = ((int)clr)&255;
                }
            } else {
                data[data_index + R] = 255;
                data[data_index + G] = 0;
                data[data_index + B] = 255;
            }
        }
    }
}

