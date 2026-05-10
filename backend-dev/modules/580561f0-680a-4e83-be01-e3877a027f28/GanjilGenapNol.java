/* Program: GanjilGenapNol
 * Deskripsi: Menentukan suatu bilangan merupakan bilangan ganjil atau genap
 * Nama: Muhammad Saiful Islam/141524020
 * Tanggal/versi: 3 November 2015/v1.0
 */

public class GanjilGenapNol {
    public String ganjilGenapNol(int bilangan) {
        if (bilangan == 0) {
            return "Nol";
        } else if (bilangan % 2 == 1) {
            return "Ganjil";
        } else {
            return "Genap";
        }
    }
}
