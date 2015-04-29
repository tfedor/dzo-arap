#include <cstdio>

extern "C" void project(int * a) {
    printf("%i\n", a[0 + 0*3]);
    printf("%i\n", a[1 + 0*3]);
    printf("%i\n", a[2 + 0*3]);

    printf("%i\n", a[0 + 1*3]);
    printf("%i\n", a[1 + 1*3]);
    printf("%i\n", a[2 + 1*3]);

    a[0 + 0*3] += 1;
    a[1 + 0*3] += 1;
    a[2 + 0*3] += 1;
    a[0 + 1*3] += 1;
    a[1 + 1*3] += 1;
    a[2 + 1*3] += 1;
}
