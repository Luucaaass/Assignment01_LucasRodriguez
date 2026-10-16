import csv
import statistics
from collections import defaultdict
import matplotlib.pyplot as plt

def compute_iqr(values):
    if len(values) < 4:
        return max(values) - min(values) if values else 0.0
    qs = statistics.quantiles(values, n=4)
    return qs[2] - qs[0]

def main():
    grouped_time = defaultdict(list)
    grouped_mem = defaultdict(list)
    status_map = {}

    with open("results/raw_measurements.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["language"], int(row["n"]), row["memory_metric"])
            status = row["status"]
            status_map[key] = status
            if status == "OK":
                grouped_time[key].append(float(row["time_sec"]))
                grouped_mem[key].append(float(row["memory_mb"]))

    summary_rows = []
    for (lang, n, metric), status in sorted(status_map.items(), key=lambda x: (x[0][0], x[0][1])):
        if status == "OK":
            times = grouped_time[(lang, n, metric)]
            mems = grouped_mem[(lang, n, metric)]
            med_t = statistics.median(times)
            iqr_t = compute_iqr(times)
            med_m = statistics.median(mems)
            iqr_m = compute_iqr(mems)
            summary_rows.append([lang, n, len(times), f"{med_t:.6f}", f"{iqr_t:.6f}", f"{med_m:.3f}", f"{iqr_m:.3f}", metric, "OK"])
        else:
            summary_rows.append([lang, n, 0, "NA", "NA", "NA", "NA", metric, status])

    with open("results/summary_table.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["language", "n", "reps", "median_time_s", "iqr_time_s", "median_mem_mb", "iqr_mem_mb", "memory_metric", "status"])
        writer.writerows(summary_rows)

    # Gráfica 1: Tiempo de ejecución vs Tamaño de matriz (Log-Log)
    plt.figure(figsize=(7, 5))
    for lang in ["C", "Java", "Python"]:
        ns = [k[1] for k in grouped_time if k[0] == lang]
        ns.sort()
        meds = [statistics.median(grouped_time[(lang, n, "Managed_Heap_MB" if lang=="Java" else "Peak_RSS_MB")]) for n in ns]
        if ns:
            plt.plot(ns, meds, marker="o", label=lang)
    plt.xscale("log", base=2)
    plt.yscale("log", base=10)
    plt.xlabel("Matrix Side Length n (log2 scale)")
    plt.ylabel("Median Execution Time [s] (log10 scale)")
    plt.title("Kernel Execution Time vs. Matrix Size (Triple-Loop i-j-k)")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/runtime_scaling.png", dpi=300)

    # Gráfica 2: Uso de memoria vs Tamaño de matriz
    plt.figure(figsize=(7, 5))
    for lang in ["C", "Java", "Python"]:
        metric = "Managed_Heap_MB" if lang == "Java" else "Peak_RSS_MB"
        ns = [k[1] for k in grouped_mem if k[0] == lang]
        ns.sort()
        meds = [statistics.median(grouped_mem[(lang, n, metric)]) for n in ns]
        if ns:
            plt.plot(ns, meds, marker="s", label=f"{lang} ({metric})")
    plt.xlabel("Matrix Side Length n")
    plt.ylabel("Median Memory Usage [MB]")
    plt.title("Measured Memory Usage vs. Matrix Size")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/memory_scaling.png", dpi=300)
    print("Resumen estadístico y gráficas generados en 'results/'.")

if __name__ == "__main__":
    main()