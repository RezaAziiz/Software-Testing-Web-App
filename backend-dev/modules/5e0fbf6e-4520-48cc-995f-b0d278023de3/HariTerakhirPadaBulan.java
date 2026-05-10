/* Program: Hari Terakhir Dari Sebuah bulan
 * Deskripsi: Menentukan hari terakhir pada bulan dan tahun tertentu
 * Author: Najib Alimudin Fajri/221524053
 * Tanggal/versi: 21 Juni 2024/v.0
 */

 public class HariTerakhirPadaBulan {
    public int hariTerakhirPadaBulan(int bulan, int tahun) {
        if (bulan == 1 || bulan == 3 || bulan == 5 || bulan == 7 || bulan == 8 || bulan == 10 || bulan == 12) {
            return 31;
        } else if (bulan == 4 || bulan == 6 || bulan == 9 || bulan == 11) {
            return 30;
        } else if (bulan == 2) {
            if ((tahun % 4 == 0 && tahun % 100 != 0) || tahun % 400 == 0) {
                return 29;
            } else {
                return 28;
            }
        }
        return 0;
    }
}
