public class SeleksiBeasiswa {

    public String prosesSeleksi(int n) {
        String logSeleksi = "";

        for (int i = 1; i <= n; i++) {
            
            // IF Pertama (Kondisi Utama)
            if (i % 2 == 0) {
                logSeleksi += "Peserta " + i + " -> Lolos Berkas\n";
                
                // IF Kedua (Nested IF di dalam IF pertama, tanpa Else)
                if (i % 4 == 0) {
                    logSeleksi += "Peserta " + i + " -> Kandidat Utama\n";
                }
            }
            
        }

        return logSeleksi;
    }
}