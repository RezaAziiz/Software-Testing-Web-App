public class LevelFourComplexity {
    /**
     * Mengembalikan jumlah perintah yang berhasil diproses,
     * atau -1 jika dibatalkan (ABORT).
     */
    public int processMedium(String commandStr, int maxRows, int maxCols) {
        int processedCount = 0;
        // TINGKAT 1: for
        MAIN_FOR: for (int i = 0; i < maxRows; i++) {
            int j = 0;
            // TINGKAT 2: do-while
            do {
                // TINGKAT 3: if
                if (j < commandStr.length()) {
                    char cmd = commandStr.charAt(j);
                    // TINGKAT 4: switch
                    switch (cmd) {
                        case 'S': // Karakter 'S' untuk SKIP
                            j++;
                            // CFG menembus 2 blok ke atas menuju kondisi do-while (j < maxCols)
                            continue;
                        case 'N': // Karakter 'N' untuk NEXT_ROW
                            processedCount++;
                            // CFG menembus 3 blok ke atas, memicu iterasi i++ pada MAIN_FOR
                            continue MAIN_FOR;
                        case 'H': // Karakter 'H' untuk HALT
                            // CFG membatalkan loop terluar (MAIN_FOR) dan melompat ke akhir fungsi
                            break MAIN_FOR;
                        case 'A': // Karakter 'A' untuk ABORT
                            // CFG langsung keluar dari fungsi seutuhnya dan mengembalikan -1
                            return -1;
                        default:
                            processedCount++;
                            // break normal milik switch, CFG menunjuk ke luar blok switch (j++)
                            break;
                    }
                }
                j++;
            } while (j < maxCols); // Evaluasi Tingkat 2
        }
        return processedCount;
    }
}