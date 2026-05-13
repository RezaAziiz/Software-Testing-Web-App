/* Program: Hitung Bilangan Genap dari 1 sampai N
 * Deskripsi: Menghitung jumlah bilangan genap dalam range tertentu
 * Tingkat Kesulitan: Mudah
 * Tipe Return: int
 * Parameter: int (batas akhir)
 */

public class HitungBilanganGenapRange {
    public int hitungBilanganGenapRange(int batas) {
        int count = 0;
        for (int i = 1; i <= batas; i++) {
            if (i % 2 == 0) {
                count = count + 1;
            }
        }
        return count;
    }
}