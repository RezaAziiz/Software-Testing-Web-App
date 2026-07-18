public class PenentuanKelulusan {
    public String penentuanKelulusan(int nilaiUts, int nilaiUas, int kehadiran, int tugas) {
        String hasil = "Tidak Lulus";
        if (nilaiUts >= 75) { // level 1
            if (nilaiUas >= 75) { // level 2
                if (kehadiran >= 80) { // level 2
                    if (tugas >= 80) { // level 3
                        hasil = "Lulus dengan baik";
                    }
                }
            }
        }
        return hasil;
    }
}
