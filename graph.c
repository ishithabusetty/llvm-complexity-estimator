// sample6.c — graph algorithms (high complexity)
#include <stdlib.h>
#include <string.h>

#define MAX 100

int visited[MAX];
int graph[MAX][MAX];

// BFS — queue, 2 loops, high memOps
void bfs(int start, int n) {
    int queue[MAX], front = 0, rear = 0;
    memset(visited, 0, sizeof(visited));
    queue[rear++] = start;
    visited[start] = 1;
    while (front < rear) {
        int node = queue[front++];
        for (int i = 0; i < n; i++)
            if (graph[node][i] && !visited[i]) {
                visited[i] = 1;
                queue[rear++] = i;
            }
    }
}

// DFS — recursive, high call count
void dfs(int node, int n) {
    visited[node] = 1;
    for (int i = 0; i < n; i++)
        if (graph[node][i] && !visited[i])
            dfs(i, n);
}

// Floyd-Warshall — triple nested, O(n^3)
void floydWarshall(int dist[][MAX], int n) {
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if (dist[i][k] + dist[k][j] < dist[i][j])
                    dist[i][j] = dist[i][k] + dist[k][j];
}

// Dijkstra — nested loops + branches
void dijkstra(int src, int n) {
    int dist[MAX], sptSet[MAX];
    for (int i = 0; i < n; i++) { dist[i] = 99999; sptSet[i] = 0; }
    dist[src] = 0;
    for (int c = 0; c < n - 1; c++) {
        int u = -1;
        for (int v = 0; v < n; v++)
            if (!sptSet[v] && (u == -1 || dist[v] < dist[u]))
                u = v;
        sptSet[u] = 1;
        for (int v = 0; v < n; v++)
            if (!sptSet[v] && graph[u][v] && dist[u] + graph[u][v] < dist[v])
                dist[v] = dist[u] + graph[u][v];
    }
}
