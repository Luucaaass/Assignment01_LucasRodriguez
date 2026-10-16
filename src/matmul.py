import sys
import struct
import time

def load_matrix(filename, n):
    with open(filename, "rb") as f:
        data = struct.unpack(f"<{n*n}d", f.read(n * n * 8))
    return [list(data[i * n : (i + 1) * n]) for i in range(n)]

def save_matrix(filename, matrix, n):
    flat = [val for row in matrix for val in row]
    with open(filename, "wb") as f:
        f.write(struct.pack(f"<{n*n}d", *flat))

def matmul_ijk(A, B, C, n):
    for i in range(n):
        row_a = A[i]
        row_c = C[i]
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += row_a[k] * B[k][j]
            row_c[j] = s

def get_peak_rss_mb():
    try:
        import resource
        ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return ru / (1024.0 * 1024.0) if sys.platform == "darwin" else ru / 1024.0
    except ImportError:
        try:
            import psutil
            return psutil.Process().memory_info().rss / (1024.0 * 1024.0)
        except ImportError:
            return 0.0

def main():
    if len(sys.argv) < 6:
        sys.exit(1)
        
    n = int(sys.argv[1])
    file_a = sys.argv[2]
    file_b = sys.argv[3]
    warmup = int(sys.argv[4])
    reps = int(sys.argv[5])
    file_out = sys.argv[6] if len(sys.argv) >= 7 else None

    A = load_matrix(file_a, n)
    B = load_matrix(file_b, n)
    C = [[0.0] * n for _ in range(n)]

    for _ in range(warmup):
        matmul_ijk(A, B, C, n)

    for r in range(reps):
        start = time.perf_counter()
        matmul_ijk(A, B, C, n)
        end = time.perf_counter()

        elapsed = end - start
        mem_mb = get_peak_rss_mb()
        mid = (n * n) // 2
        checksum = C[0][0] + C[mid // n][mid % n] + C[n - 1][n - 1]
        print(f"RESULT,{r + 1},{elapsed:.9f},{mem_mb:.3f},{checksum:.6f}", flush=True)

    if file_out:
        save_matrix(file_out, C, n)

if __name__ == "__main__":
    main()