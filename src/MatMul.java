import java.io.*;
import java.nio.*;
import java.nio.channels.FileChannel;
import java.util.Locale;

public class MatMul {
    public static double[][] loadMatrix(String filename, int n) throws IOException {
        double[][] matrix = new double[n][n];
        try (FileInputStream fis = new FileInputStream(filename);
             FileChannel channel = fis.getChannel()) {
            ByteBuffer buffer = ByteBuffer.allocateDirect(n * n * 8).order(ByteOrder.nativeOrder());
            while (buffer.hasRemaining()) {
                if (channel.read(buffer) == -1) break;
            }
            buffer.flip();
            DoubleBuffer db = buffer.asDoubleBuffer();
            for (int i = 0; i < n; i++) {
                db.get(matrix[i], 0, n);
            }
        }
        return matrix;
    }

    public static void saveMatrix(String filename, double[][] matrix, int n) throws IOException {
        try (FileOutputStream fos = new FileOutputStream(filename);
             FileChannel channel = fos.getChannel()) {
            ByteBuffer buffer = ByteBuffer.allocateDirect(n * n * 8).order(ByteOrder.nativeOrder());
            DoubleBuffer db = buffer.asDoubleBuffer();
            for (int i = 0; i < n; i++) {
                db.put(matrix[i]);
            }
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }
        }
    }

    public static void matmulIjk(double[][] A, double[][] B, double[][] C, int n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                double sum = 0.0;
                for (int k = 0; k < n; k++) {
                    sum += A[i][k] * B[k][j];
                }
                C[i][j] = sum;
            }
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 5) {
            System.err.println("Uso: java MatMul <n> <A.bin> <B.bin> <warmup> <reps> [out.bin]");
            System.exit(1);
        }
        int n = Integer.parseInt(args[0]);
        String fileA = args[1];
        String fileB = args[2];
        int warmup = Integer.parseInt(args[3]);
        int reps = Integer.parseInt(args[4]);
        String fileOut = (args.length >= 6) ? args[5] : null;

        double[][] A = loadMatrix(fileA, n);
        double[][] B = loadMatrix(fileB, n);
        double[][] C = new double[n][n];

        for (int w = 0; w < warmup; w++) {
            matmulIjk(A, B, C, n);
        }

        Runtime rt = Runtime.getRuntime();
        for (int r = 0; r < reps; r++) {
            long start = System.nanoTime();
            matmulIjk(A, B, C, n);
            long end = System.nanoTime();

            double elapsed = (end - start) * 1e-9;
            double usedHeapMb = (rt.totalMemory() - rt.freeMemory()) / (1024.0 * 1024.0);
            int mid = (n * n) / 2;
            double checksum = C[0][0] + C[mid / n][mid % n] + C[n - 1][n - 1];
            System.out.printf(Locale.US, "RESULT,%d,%.9f,%.3f,%.6f%n", r + 1, elapsed, usedHeapMb, checksum);
        }

        if (fileOut != null) {
            saveMatrix(fileOut, C, n);
        }
    }
}