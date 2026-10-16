import os
import sys
import subprocess
import struct
import math
import csv

SIZES = [10, 64, 128, 256, 512, 1024]
REPS = 5
TIMEOUT_PER_RUN_SEC = 120.0
ABS_TOL = 1e-12
REL_TOL = 1e-9

IS_WIN = sys.platform.startswith("win")
C_EXEC = os.path.join("bin", "matmul_c.exe" if IS_WIN else "matmul_c")

def read_flat_bin(filepath, n):
    with open(filepath, "rb") as f:
        return struct.unpack(f"<{n*n}d", f.read(n * n * 8))

def verify_matrices(calc, ref, n):
    max_diff = 0.0
    for a, b in zip(calc, ref):
        diff = abs(a - b)
        if diff > max_diff:
            max_diff = diff
        if not math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL):
            return False, max_diff
    return True, max_diff

def compile_sources():
    os.makedirs("bin", exist_ok=True)
    c_cmd = ["gcc", "-O2", "-std=c11", "-Wall", "src/matmul.c", "-o", C_EXEC]
    if IS_WIN:
        c_cmd.append("-lpsapi")
    subprocess.run(c_cmd, check=True)
    subprocess.run(["javac", "-d", "bin", "src/MatMul.java"], check=True)
    print("Compilación completada.")

def get_cmd(lang, n, file_a, file_b, warmup, reps, file_out=None):
    if lang == "C":
        cmd = [C_EXEC, str(n), file_a, file_b, str(warmup), str(reps)]
    elif lang == "Java":
        cmd = ["java", "-Xms256m", "-Xmx4g", "-cp", "bin", "MatMul", str(n), file_a, file_b, str(warmup), str(reps)]
    elif lang == "Python":
        cmd = [sys.executable, "src/matmul.py", str(n), file_a, file_b, str(warmup), str(reps)]
    if file_out:
        cmd.append(file_out)
    return cmd

def validate_correctness():
    print("Verificando corrección en los 3 lenguajes...")
    os.makedirs("results", exist_ok=True)
    val_rows = []
    for lang in ["C", "Java", "Python"]:
        out_id = f"data/out_{lang}_I10.bin"
        subprocess.run(get_cmd(lang, 10, "data/A_10.bin", "data/I_10.bin", 0, 1, out_id), check=True, stdout=subprocess.DEVNULL)
        ok_id, diff_id = verify_matrices(read_flat_bin(out_id, 10), read_flat_bin("data/A_10.bin", 10), 10)

        out_z = f"data/out_{lang}_Z10.bin"
        subprocess.run(get_cmd(lang, 10, "data/A_10.bin", "data/Z_10.bin", 0, 1, out_z), check=True, stdout=subprocess.DEVNULL)
        ok_z, diff_z = verify_matrices(read_flat_bin(out_z, 10), read_flat_bin("data/Z_10.bin", 10), 10)

        out_r = f"data/out_{lang}_64.bin"
        subprocess.run(get_cmd(lang, 64, "data/A_64.bin", "data/B_64.bin", 0, 1, out_r), check=True, stdout=subprocess.DEVNULL)
        ok_r, diff_r = verify_matrices(read_flat_bin(out_r, 64), read_flat_bin("data/C_ref_64.bin", 64), 64)

        val_rows.append([lang, ok_id, f"{diff_id:.3e}", ok_z, f"{diff_z:.3e}", ok_r, f"{diff_r:.3e}"])
        if not (ok_id and ok_z and ok_r):
            raise RuntimeError(f"Fallo de validación en {lang}")

    with open("results/correctness_validation.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["language", "identity_ok", "identity_max_err", "zero_ok", "zero_max_err", "random64_ok", "random64_max_err"])
        writer.writerows(val_rows)
    print("Todas las validaciones superadas.")

def run_experiments():
    raw_file = "results/raw_measurements.csv"
    with open(raw_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["language", "n", "numeric_type", "threads", "warmup", "rep", "time_sec", "memory_mb", "memory_metric", "checksum", "status"])

        for lang in ["C", "Java", "Python"]:
            warmup = 2 if lang == "Java" else 1
            mem_metric = "Managed_Heap_MB" if lang == "Java" else "Peak_RSS_MB"
            timed_out_lang = False

            for n in SIZES:
                if timed_out_lang:
                    writer.writerow([lang, n, "float64", 1, warmup, 0, "NA", "NA", mem_metric, "NA", "SKIPPED_AFTER_TIMEOUT"])
                    continue

                print(f"Ejecutando {lang} con n={n}...")
                cmd = get_cmd(lang, n, f"data/A_{n}.bin", f"data/B_{n}.bin", warmup, REPS)
                total_timeout = TIMEOUT_PER_RUN_SEC * (warmup + REPS)
                try:
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=total_timeout, check=True)
                    for line in proc.stdout.strip().splitlines():
                        if line.startswith("RESULT,"):
                            _, rep, t_sec, mem_mb, chk = line.split(",")
                            writer.writerow([lang, n, "float64", 1, warmup, rep, t_sec, mem_mb, mem_metric, chk, "OK"])
                except subprocess.TimeoutExpired:
                    print(f"  [!] TIMEOUT alcanzado en {lang} para n={n}.")
                    writer.writerow([lang, n, "float64", 1, warmup, 0, "NA", "NA", mem_metric, "NA", "TIMEOUT"])
                    timed_out_lang = True

if __name__ == "__main__":
    compile_sources()
    validate_correctness()
    run_experiments()