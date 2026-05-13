public class PemrosesanPaket {

    public String prosesPaket(int n) {
        String logPaket = "";

        for (int i = 1; i <= n; i++) {
            
            // Variabel bantu agar log lebih rapi
            String kategori = "";
            String kemasan = "";

            // Struktur Kontrol 1: Pengecekan Kategori (if - else if - else)
            if (i % 3 == 0) {
                kategori = "Berat";
            } else if (i % 2 == 0) {
                kategori = "Sedang";
            } else {
                kategori = "Ringan";
            }

            // Struktur Kontrol 2: Pengecekan Kemasan (if - else) ditulis berurutan setelah blok pertama selesai
            if (i % 5 == 0) {
                kemasan = "Khusus";
            } else {
                kemasan = "Standar";
            }
            
            // Menggabungkan hasil dari kedua pengecekan independen
            logPaket += "Paket " + i + " -> Kategori: " + kategori + ", Kemasan: " + kemasan + "\n";
        }

        return logPaket;
    }
}