/* Program: Bintang Segiempat
 * Deskripsi: Mencetak bintang dalam bentuk segiempat
 * Tingkat Kesulitan: Mudah
 * Tipe Return: void
 * Parameter: int (ukuran segiempat)
 */

public class BintangSegiEmpat {
    public String bintangSegiEmpat(int N) {
        String hasil = "";
        for (int i = 1; i <= N; i++) {
            for (int j = 1; j <= N; j++) {
                hasil += "* ";
            }
            hasil += "\n";
        }

        return hasil;
    }
}