/* Deskripsi:
 * Menghitung total skor inspeksi produk.
 * Hanya produk dengan ID genap yang diperiksa.
 * Setiap produk melalui 3 tahap inspeksi.
 * Jika kombinasi ID produk dan tahap inspeksi memenuhi syarat,
 * maka dilakukan pemeriksaan terhadap 3 komponen.
 * Komponen ke-2 dilewati karena tidak memerlukan inspeksi.
 * Pemeriksaan komponen dihentikan apabila total skor inspeksi
 * telah melebihi batas maksimum.
 */
public class EvaluasiKualitasProduk {

    public int evaluasiKualitasProduk(int jumlahProduk) {
        int totalSkor = 0;

        for (int idProduk = 1; idProduk <= jumlahProduk; idProduk++) {
            if (idProduk % 2 == 0) {
                int tahapInspeksi = 1;

                while (tahapInspeksi <= 3) {
                    if ((idProduk + tahapInspeksi) % 2 == 0) {
                        int komponen = 1;
                        do {
                            if (komponen == 2) {
                                komponen++;
                                continue;
                            }
                            totalSkor += idProduk * tahapInspeksi * komponen;
                            if (totalSkor > 100) {
                                break;
                            }
                            komponen++;
                        } while (komponen <= 3);
                    }
                    tahapInspeksi++;
                }
            }
        }

        return totalSkor;
    }
}