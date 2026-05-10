/* Program: Nilai Mutu
 * Deskripsi: Menentukan nilai mutu berdasarkan performa akademik mahasiswa
 * Tingkat Kesulitan: Mudah
 * Tipe Return: char
 * Parameter: double (nilai UTS), double (nilai UAS), double (nilai Tugas), int (jumlah kehadiran)
 */

public class NilaiMutu {
    public char nilaiMutu(float uts, float uas, float tugas, int hadir) {
        char nilaiMutu = ' ';
        float nilai, nilaiHadir;
        nilaiHadir = (float) hadir / 14 * 100;
        nilai = (float) ((0.3 * uts) + (0.4 * uas) + (0.2 * tugas) + (0.1 * nilaiHadir));

        if (nilai >= 85) {
            nilaiMutu = 'A';
        } else if (nilai >= 70) {
            nilaiMutu = 'B';
        } else if (nilai >= 55) {
            nilaiMutu = 'C';
        } else if (nilai >= 40) {
            nilaiMutu = 'D';
        } else {
            nilaiMutu = 'E';
        }
        return nilaiMutu;
    }
}