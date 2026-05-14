public class PengecekanSensor {

    public String analisaSensor(int n) {
        String hasilCek = "";

        for (int i = 1; i <= n; i++) {

            if (i % 2 == 0) {
                // Nested Branching 1: Evaluasi kondisi Sensor Suhu (Genap)
                if (i % 4 == 0) {
                    hasilCek += "Sensor " + i + " -> Suhu: Overheating\n";
                } else {
                    hasilCek += "Sensor " + i + " -> Suhu: Normal\n";
                }
            } else {
                // Nested Branching 2: Evaluasi kondisi Sensor Kelembapan (Ganjil)
                if (i % 3 == 0) {
                    hasilCek += "Sensor " + i + " -> Kelembapan: Kritis\n";
                } else {
                    hasilCek += "Sensor " + i + " -> Kelembapan: Normal\n";
                }
            }
        }

        return hasilCek;
    }
}