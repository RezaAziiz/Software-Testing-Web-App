/**
 * Memproses rangkaian perintah navigasi robot pada area berbentuk grid.
 *
 * Robot bergerak per baris (for), sedangkan setiap kolom pada baris tersebut
 * diproses menggunakan do-while berdasarkan karakter pada commandSequence.
 *
 * Nilai yang dikembalikan adalah jumlah perintah yang berhasil diproses.
 * Jika ditemukan perintah ABORT ('A'), misi langsung dibatalkan dan
 * method mengembalikan -1.
 */
public class RobotMissionProcessor {
    public int processMission(String commandSequence, int totalRows, int totalCols) {

        int processedCommands = 0;

        // TINGKAT 1: for
        MAIN_FOR: for (int row = 0; row < totalRows; row++) {
            int col = 0;
            // TINGKAT 2: do-while
            do {
                // TINGKAT 3: if
                if (col < commandSequence.length()) {
                    char command = commandSequence.charAt(col);
                    // TINGKAT 4: switch
                    switch (command) {
                        case 'S': // Skip posisi saat ini
                            col++;
                            // Lanjut ke evaluasi kondisi do-while
                            continue;
                        case 'N': // Pindah ke baris berikutnya
                            processedCommands++;
                            // Langsung lanjut ke iterasi berikutnya pada loop utama
                            continue MAIN_FOR;
                        case 'H': // Hentikan misi
                            // Keluar dari loop utama, kemudian mengembalikan hasil
                            break MAIN_FOR;
                        case 'A': // Batalkan misi
                            // Keluar langsung dari method
                            return -1;
                        default:
                            // Perintah biasa berhasil diproses
                            processedCommands++;
                            // Keluar dari switch
                            break;
                    }
                }
                col++;
            } while (col < totalCols);
        }
        return processedCommands;
    }
}