// sample3.c — nested loops, structs, pointers

typedef struct { float x, y, z; } Vec3;

float dot(Vec3 a, Vec3 b) {
    return a.x*b.x + a.y*b.y + a.z*b.z;
}

void normalize(Vec3 *v) {
    float len = v->x*v->x + v->y*v->y + v->z*v->z;
    if (len > 0.0f) {
        len = 1.0f / len;
        v->x *= len;
        v->y *= len;
        v->z *= len;
    }
}

void transformPoints(Vec3 *pts, int n, float scale) {
    for (int i = 0; i < n; i++) {
        pts[i].x *= scale;
        pts[i].y *= scale;
        pts[i].z *= scale;
        normalize(&pts[i]);
    }
}

int searchMatrix(int mat[][32], int rows, int target) {
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < 32; j++)
            if (mat[i][j] == target) return i * 32 + j;
    return -1;
}
