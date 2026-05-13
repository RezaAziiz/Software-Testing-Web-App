/* Program: Cek Sisi Segitiga
 * Deskripsi: Mengecek teorema segitiga pada suatu bidang
 * Author: Najib Alimudin Fajri/221524053
 * Tanggal/versi: 21 Juni 2024/v.0
 * Formula: Segitiga ≡ (a + b > c) ∩ (a + c > b) ∩ (b + c > a)
 */

 public class CekSisiSegitiga {
    public boolean cekSisiSegitiga(int sisiSatu, int sisiDua, int sisiTiga) {
        if (sisiSatu + sisiDua > sisiTiga) {
            if (sisiSatu + sisiTiga > sisiDua) {
                if (sisiDua + sisiTiga > sisiSatu) {
                    return true;
                }
            }
        }
        return false;
    }
}
