// sample2.c — branching and pointer functions

int fibonacci(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        int tmp = a + b;
        a = b;
        b = tmp;
    }
    return b;
}

void copyArray(int *src, int *dst, int n) {
    for (int i = 0; i < n; i++)
        dst[i] = src[i];
}

int classify(int x) {
    if (x < 0)   return -1;
    if (x == 0)  return  0;
    if (x < 10)  return  1;
    if (x < 100) return  2;
    return 3;
}
