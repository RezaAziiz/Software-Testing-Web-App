public class HitungBonusKaryawan {

    public int hitungBonusKaryawan(int jumlahKaryawan) {
        int totalBonus = 0;

        for (int idKaryawan = 1; idKaryawan <= jumlahKaryawan; idKaryawan++) {
            if (idKaryawan % 2 == 0) {

                int bulan = 1;

                while (bulan <= 3) {
                    if ((idKaryawan + bulan) % 2 == 0) {
                        totalBonus += idKaryawan * bulan;
                    }

                    bulan++;
                }
            }
        }

        return totalBonus;
    }
}