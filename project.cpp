#include <cstdio>
#include <cmath>
#include <algorithm>

#define R (0)
#define G (1)
#define B (2)

extern "C" void clear(char * data, int width, int height) {

    for (int i=0; i<width*height*3; i++) {
        data[i] = 255;
    }

}

void dot(double * homography, int x, int y, double &rx, double &ry) {
    double rw;

    rx = homography[0]*x + homography[1]*y + homography[2];
    ry = homography[3]*x + homography[4]*y + homography[5];
    rw = homography[6]*x + homography[7]*y + homography[8];

    rx /= rw;
    ry /= rw;
}

extern "C" void project(double * homography, char * orig, char * data, int width, int height, int * borders, int border_y_start, int border_y_end) {

    int max_index = height*width*3;

    int bi = 0;
    for (int y=border_y_start; y<border_y_end; y++) {

        for (int x=borders[bi]; x<=borders[bi+1]; x++) {

            double rx, ry;
            dot(homography, x, y, rx, ry);

            int data_index = y*width*3 + x*3;

            //
            /*
            int lft = floor(rx);
            int rgt = ceil(rx);

            int top = floor(ry);
            int btm = ceil(ry);

            if (lft >= 0 && rgt < width && top >= 0 && btm < height) {
                double coefX = rx-(double)lft;
                double coefY = ry-(double)top;

                double tl = (1-coefX)*(1-coefY);
                double tr = coefX*(1-coefY);
                double bl = (1-coefX)*coefY;
                double br = coefX*coefY;

                data[data_index + R] = std::min(255, (int)round(
                                       tl*orig[top*width*3 + lft*3 + R]
                                     + tr*orig[top*width*3 + rgt*3 + R]
                                     + bl*orig[btm*width*3 + lft*3 + R]
                                     + br*orig[btm*width*3 + rgt*3 + R]));

                data[data_index + G] = std::min(255, (int)round(
                                       tl*orig[top*width*3 + lft*3 + G]
                                     + tr*orig[top*width*3 + rgt*3 + G]
                                     + bl*orig[btm*width*3 + lft*3 + G]
                                     + br*orig[btm*width*3 + rgt*3 + G]));

                data[data_index + B] = std::min(255, (int)round(
                                       tl*orig[top*width*3 + lft*3 + B]
                                     + tr*orig[top*width*3 + rgt*3 + B]
                                     + bl*orig[btm*width*3 + lft*3 + B]
                                     + br*orig[btm*width*3 + rgt*3 + B]));
            } else {
                data[data_index + R] = 0;
                data[data_index + G] = 0;
                data[data_index + B] = 0;
            }
            */
            //

            int xn = round(rx);
            int yn = round(ry);
            int orig_index = yn*width*3 + xn*3;

            if (orig_index < 0 || orig_index >= max_index) {
                data[data_index + R] = 255;
                data[data_index + G] = 255;
                data[data_index + B] = 255;
            } else {
                data[data_index + R] = orig[orig_index + R];
                data[data_index + G] = orig[orig_index + G];
                data[data_index + B] = orig[orig_index + B];
            }
        }

        bi += 2;
    }
}