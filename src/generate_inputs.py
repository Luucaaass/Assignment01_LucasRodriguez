import os
import struct
import random

SEED = 42
SIZES = [10, 64, 128, 256, 512, 1024]
DATA_DIR = "data"

def generate_matrix(n, rng):
    return [rng.uniform(-1.0, 1.0) for _ in range(n * n)]

def save_matrix(filepath, matrix):
    with open(filepath, "wb") as f:
        f.write(struct.pack(f"<{len(matrix)}d", *matrix))

def multiply_ref(A, B, n):
    C = [0.0] * (n * n)
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += A[i * n + k] * B[k * n + j]
            C[i * n + j] = s
    return C

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Casos de prueba de validación (Identidad y Cero para n=10)
    n_val = 10
    rng = random.Random(SEED)
    A_val = generate_matrix(n_val, rng)
    I_val = [1.0 if i == j else 0.0 for i in range(n_val) for j in range(n_val)]
    Z_val = [0.0] * (n_val * n_val)
    
    save_matrix(os.path.join(DATA_DIR, "A_10.bin"), A_val)
    save_matrix(os.path.join(DATA_DIR, "I_10.bin"), I_val)
    save_matrix(os.path.join(DATA_DIR, "Z_10.bin"), Z_val)
    
    # 2. Matrices para benchmarking y referencia de validación
    for n in SIZES:
        rng = random.Random(SEED + n)
        A = generate_matrix(n, rng)
        B = generate_matrix(n, rng)
        save_matrix(os.path.join(DATA_DIR, f"A_{n}.bin"), A)
        save_matrix(os.path.join(DATA_DIR, f"B_{n}.bin"), B)
        
        if n <= 128:
            C_ref = multiply_ref(A, B, n)
            save_matrix(os.path.join(DATA_DIR, f"C_ref_{n}.bin"), C_ref)
            
    print("Matrices de entrada y referencias generadas correctamente en 'data/'.")

if __name__ == "__main__":
    main()