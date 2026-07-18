public class HitungInsentifKaryawan {

    public int hitungInsentifKaryawan(int jumlahKaryawan) {
        int totalInsentif = 0;

        for (int idKaryawan = 1; idKaryawan <= jumlahKaryawan; idKaryawan++) {
            if (idKaryawan % 2 == 0) {
                int periode = 1;
                while (periode <= 2) {
                    if ((idKaryawan + periode) % 2 == 0) {
                        int pencapaian = 1;
                        do {
                            if (pencapaian % 2 == 1) {
                                totalInsentif += idKaryawan * periode * pencapaian;
                            }
                            pencapaian++;
                        } while (pencapaian <= 2);
                    }
                    periode++;
                }
            }
        }

        return totalInsentif;
    }
}