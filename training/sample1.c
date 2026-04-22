// sample1.c — simple arithmetic functions

int add(int a, int b) {
    return a + b;
}

int sumArray(int *arr, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++)
        sum += arr[i];
    return sum;
}

void matMul(int A[16][16], int B[16][16], int C[16][16]) {
    for (int i = 0; i < 16; i++)
        for (int j = 0; j < 16; j++) {
            C[i][j] = 0;
            for (int k = 0; k < 16; k++)
                C[i][j] += A[i][k] * B[k][j];
        }
}
