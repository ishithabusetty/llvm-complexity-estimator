// sample5.c — deeply nested loops for stress testing loop depth feature

void deepNest(int arr[4][4][4], int val) {
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            for (int k = 0; k < 4; k++)
                arr[i][j][k] = val + i + j + k;
}

void tensorOp(float A[8][8][8], float B[8][8][8], float C[8][8][8]) {
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8; j++)
            for (int k = 0; k < 8; k++)
                C[i][j][k] = A[i][j][k] * B[i][j][k];
}

int maxIn3D(int cube[4][4][4]) {
    int m = cube[0][0][0];
    for (int i = 0; i < 4; i++)
        for (int j = 0; j < 4; j++)
            for (int k = 0; k < 4; k++)
                if (cube[i][j][k] > m) m = cube[i][j][k];
    return m;
}
