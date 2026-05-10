public class KlasifikasiProduk {

    public String cekProduk(int n) {
        String hasilKlasifikasi = "";

        for (int i = 1; i <= n; i++) {
            
            // Kondisi Utama
            if (i % 5 == 0) {
                hasilKlasifikasi += "Produk " + i + " -> Kualitas Premium\n";
            } else {
                
                // Nested IF di dalam blok Else
                if (i % 2 == 0) {
                    hasilKlasifikasi += "Produk " + i + " -> Kualitas Standar\n";
                } else {
                    hasilKlasifikasi += "Produk " + i + " -> Kualitas Rendah\n";
                }
                
            }
        }

        return hasilKlasifikasi;
    }
} 
    

