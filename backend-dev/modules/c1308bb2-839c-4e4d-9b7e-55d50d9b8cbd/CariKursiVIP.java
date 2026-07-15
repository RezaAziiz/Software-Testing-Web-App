public class CariKursiVIP {

    public String cariKursi(int baris, int kolom, int vipBaris, int vipKolom) {

        String hasil = "Tidak ditemukan";
        OUTER: for (int i = 0; i < baris; i++) {
            for (int j = 0; j < kolom; j++) {
                if (i == vipBaris) {
                    if (j == vipKolom) {
                        hasil = "VIP ditemukan";
                        break OUTER;
                    }
                }
            }
        }
        return hasil;
    }
}