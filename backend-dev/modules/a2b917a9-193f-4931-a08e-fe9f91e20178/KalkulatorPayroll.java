public class KalkulatorPayroll {

    public String hitungTunjangan(int n) {
        String rekapTunjangan = "";

        // 1 Loop utama untuk memproses ID karyawan dari 1 sampai n
        for (int i = 1; i <= n; i++) {
            
            // Branching Tingkat 1: Cek Karyawan Tetap (Genap) atau Kontrak (Ganjil)
            if (i % 2 == 0) {
                // Nested Branching 1: Evaluasi Karyawan Tetap
                if (i % 4 == 0) {
                    rekapTunjangan += "ID " + i + ": Tunjangan Penuh\n";
                } else {
                    rekapTunjangan += "ID " + i + ": Tunjangan Standar\n";
                }
            } else {
                // Nested Branching 2: Evaluasi Karyawan Kontrak
                if (i % 3 == 0) {
                    rekapTunjangan += "ID " + i + ": Tunjangan Ekstra\n";
                } else {
                    rekapTunjangan += "ID " + i + ": Tunjangan Dasar\n";
                }
            }
        }
        
        return rekapTunjangan;
    }
}