#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
double get_peak_rss_mb() {
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return (double)pmc.PeakWorkingSetSize / (1024.0 * 1024.0);
    }
    return 0.0;
}
double get_time_sec() {
    LARGE_INTEGER freq, count;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&count);
    return (double)count.QuadPart / (double)freq.QuadPart;
}
#else
#include <sys/resource.h>
double get_peak_rss_mb() {
    struct rusage r_usage;
    getrusage(RUSAGE_SELF, &r_usage);
#ifdef __APPLE__
    return r_usage.ru_maxrss / (1024.0 * 1024.0);
#else
    return r_usage.ru_maxrss / 1024.0;
#endif
}
double get_time_sec() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}
#endif

void load_matrix(const char *filename, double *matrix, int n) {
    FILE *f = fopen(filename, "rb");
    if (!f) { perror("Error al abrir archivo"); exit(EXIT_FAILURE); }
    fread(matrix, sizeof(double), (size_t)n * n, f);
    fclose(f);
}

void save_matrix(const char *filename, double *matrix, int n) {
    FILE *f = fopen(filename, "wb");
    if (!f) { perror("Error al escribir archivo"); exit(EXIT_FAILURE); }
    fwrite(matrix, sizeof(double), (size_t)n * n, f);
    fclose(f);
}

void matmul_ijk(const double *A, const double *B, double *C, int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[i * n + k] * B[k * n + j];
            }
            C[i * n + j] = sum;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 6) return EXIT_FAILURE;
    int n = atoi(argv[1]);
    const char *fileA = argv[2];
    const char *fileB = argv[3];
    int warmup = atoi(argv[4]);
    int reps = atoi(argv[5]);
    const char *fileOut = (argc >= 7) ? argv[6] : NULL;

    double *A = (double *)malloc((size_t)n * n * sizeof(double));
    double *B = (double *)malloc((size_t)n * n * sizeof(double));
    double *C = (double *)malloc((size_t)n * n * sizeof(double));
    if (!A || !B || !C) return EXIT_FAILURE;

    load_matrix(fileA, A, n);
    load_matrix(fileB, B, n);

    for (int w = 0; w < warmup; w++) {
        matmul_ijk(A, B, C, n);
    }

    for (int r = 0; r < reps; r++) {
        double start = get_time_sec();
        matmul_ijk(A, B, C, n);
        double end = get_time_sec();

        double elapsed = end - start;
        double checksum = C[0] + C[(n * n) / 2] + C[n * n - 1];
        double mem_mb = get_peak_rss_mb();
        printf("RESULT,%d,%.9f,%.3f,%.6f\n", r + 1, elapsed, mem_mb, checksum);
        fflush(stdout);
    }

    if (fileOut) save_matrix(fileOut, C, n);

    free(A); free(B); free(C);
    return EXIT_SUCCESS;
}