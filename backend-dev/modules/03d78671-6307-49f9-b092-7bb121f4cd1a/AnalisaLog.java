public class AnalisaLog {

    public String klasifikasiLog(int n) {
        String hasilLog = "";

        // 1 Loop utama untuk membaca antrean log dari 1 sampai n
        for (int i = 1; i <= n; i++) {

            // Branching Tingkat 1: Cek sumber log (Backend/Genap atau Frontend/Ganjil)
            if (i % 2 == 0) {
                // Nested Branching 1: Evaluasi kondisi log Backend
                if (i % 4 == 0) {
                    hasilLog += "Log " + i + " -> Backend: Critical Error\n";
                } else {
                    hasilLog += "Log " + i + " -> Backend: Normal\n";
                }
            } else {
                // Nested Branching 2: Evaluasi kondisi log Frontend
                if (i % 5 == 0) {
                    hasilLog += "Log " + i + " -> Frontend: Timeout\n";
                } else {
                    hasilLog += "Log " + i + " -> Frontend: Normal\n";
                }
            }
        }

        return hasilLog;
    }
}