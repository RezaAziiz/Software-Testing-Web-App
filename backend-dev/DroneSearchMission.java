/**
 * Melakukan pencarian target pada area pemetaan berbentuk tiga dimensi.
 *
 * Drone memindai setiap sektor (layer), setiap baris pada sektor,
 * kemudian setiap titik pengamatan berdasarkan urutan instruksi.
 *
 * Nilai yang dikembalikan:
 * - "FOUND" : target berhasil ditemukan.
 * - "NOT_FOUND" : seluruh area telah dipindai namun target tidak ditemukan.
 */
public class DroneSearchMission {
    public String searchTarget(int totalLayers,
            int totalRows,
            int totalPoints,
            String instructionSequence) {

        // TINGKAT 1: for
        L1_OUTER: for (int layer = 0; layer < totalLayers; layer++) {
            int row = 0;
            // TINGKAT 2: while
            L2_WHILE: while (row < totalRows) {
                // TINGKAT 3: if
                if (layer + row < 500) {
                    // TINGKAT 4: switch
                    switch (row % 2) {
                        case 0:
                            int point = 0;
                            // TINGKAT 5: do-while
                            L5_DEEP_DO: do {
                                // TINGKAT 6: if-else bersarang
                                if (point < instructionSequence.length()) {
                                    char instruction = instructionSequence.charAt(point);
                                    if (instruction == 'F') {
                                        // Target berhasil ditemukan
                                        return "FOUND";
                                    } else if (instruction == 'C') {
                                        // Lanjutkan pemindaian pada titik berikutnya
                                        point++;
                                        continue L5_DEEP_DO;
                                    } else if (instruction == 'U') {
                                        // Pindah ke baris berikutnya
                                        row++;
                                        continue L2_WHILE;

                                    } else if (instruction == 'B') {

                                        // Hentikan seluruh proses pencarian
                                        break L1_OUTER;
                                    }
                                }
                                point++;
                            } while (point < totalPoints);
                            break;
                        case 1:
                            row++;
                            // Langsung lanjut ke evaluasi while
                            continue L2_WHILE;
                    }
                }
                row++;
            }
        }
        return "NOT_FOUND";
    }
}