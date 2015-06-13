#include <cstdio>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <map>
#include <bitset>
#include <queue>

#define R (0)
#define G (1)
#define B (2)

using namespace std;

extern "C" void compute_mask(bool * mask, char * orig, int width, int height, int tolerance) {

    int empty_r = orig[0]&255;
    int empty_g = orig[1]&255;
    int empty_b = orig[2]&255;

    // bounds
    int lo_r = empty_r - tolerance;
    int lo_g = empty_g - tolerance;
    int lo_b = empty_b - tolerance;

    int up_r = empty_r + tolerance;
    int up_g = empty_g + tolerance;
    int up_b = empty_b + tolerance;

    // queue
    queue<int> queue_x;
    queue<int> queue_y;

    queue_x.push(0);
    queue_y.push(0);

    // closed
    bool ** closed = new bool*[height];
    for (int i=0; i<height; i++) {
        closed[i] = new bool[width];
        memset(closed[i], false, width*sizeof(bool));
    }

    while (!queue_x.empty()) {

        int x = queue_x.front();
        int y = queue_y.front();

        queue_x.pop();
        queue_y.pop();

        if (x < 0 || x >= width || y < 0 || y >= height) { continue; }
        if (closed[y][x]) {continue;}
        closed[y][x] = true;

        int px_r = orig[(y*width + x)*3 + R] & 255;
        int px_g = orig[(y*width + x)*3 + G] & 255;
        int px_b = orig[(y*width + x)*3 + B] & 255;

        bool foreground = (px_r < lo_r || px_r > up_r
                        || px_g < lo_g || px_g > up_g
                        || px_b < lo_b || px_b > up_b);
        if (!foreground) {
            mask[y*width+x] = false;

            queue_x.push(x-1); queue_y.push(y);
            queue_x.push(x+1); queue_y.push(y);
            queue_x.push(x);   queue_y.push(y-1);
            queue_x.push(x);   queue_y.push(y+1);
        }
    }
}

/**/

extern "C" void clear(char * orig, char * data, int width, int height) {

    char r = orig[0]&255;
    char g = orig[1]&255;
    char b = orig[2]&255;

    for (int i=0; i<width*height*3; i+=3) {
        data[i]   = r;
        data[i+1] = g;
        data[i+2] = b;
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
    /*
    Bresenham's line
    http://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    */

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
extern "C" void project(double * homography, bool * mask, char * orig, char * data, int width, int height, int * corners) {

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

            //
            int lft = floor(rx);
            int rgt = lft+1;

            int top = floor(ry);
            int btm = top+1;

            int data_index = (y*width + x)*3;

            if (lft >= 0 && rgt < width && top >= 0 && btm < height) {
                if (!mask[(int)round(ry)*width + (int)round(rx)]) {
                    // data[data_index + R] = 255;
                    // data[data_index + G] = 0;
                    // data[data_index + B] = 0;
                    continue;
                }

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
                //data[data_index + R] = 255;
                //data[data_index + G] = 0;
                //data[data_index + B] = 255;
            }
        }
    }
}

