\# Assignment 1: Basic Matrix Multiplication in Python, Java and C



\*\*Author:\*\* Lucas Rodríguez  

\*\*Course:\*\* Big Data — Grado en Ciencia e Ingeniería de Datos (ULPGC)  

\*\*Academic Year:\*\* 2026–2027  



\## 1. Environment and System Specifications

\- \*\*Operating System:\*\* Windows 11 (64-bit) / PowerShell

\- \*\*C Compiler:\*\* GCC 11+ via MinGW-w64 (`gcc -O2 -std=c11 -Wall src/matmul.c -o bin/matmul\_c.exe -lpsapi`)

\- \*\*Java Virtual Machine:\*\* OpenJDK 17+ (`javac -d bin src/MatMul.java` and `java -Xms256m -Xmx4g`)

\- \*\*Python Interpreter:\*\* CPython 3.10+ (with `matplotlib` for post-processing)

\- \*\*Timer Resolution:\*\* Monotonic timers (`QueryPerformanceCounter` in C/Win32, `System.nanoTime()` in Java, `time.perf\_counter()` in Python)



\## 2. Repository Structure

```text

Assignment01\_LucasRodriguez\_Materials/

├── bin/                        # Compiled executables and Java bytecodes

├── data/                       # Generated deterministic binary test matrices

├── results/                    # Validation logs, raw runs, summary tables and plots

│   ├── correctness\_validation.csv

│   ├── raw\_measurements.csv

│   ├── summary\_table.csv

│   ├── runtime\_scaling.png

│   └── memory\_scaling.png

├── src/                        # Implementation source code

│   ├── generate\_inputs.py      # Input generator and reference verification

│   ├── matmul.c                # C naive i-j-k implementation

│   ├── MatMul.java             # Java naive i-j-k implementation

│   └── matmul.py               # Python naive i-j-k implementation

├── run\_benchmarks.py           # Benchmark harness and validation runner

├── analyze\_results.py          # Summary statistics (median, IQR) and plot generator

└── README.md                   # Build and execution guide

