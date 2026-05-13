public class NestedIfEmpat {
    public static String nestedIfEmpat(int nilaiUts, int nilaiUas, int kehadiran, int tugas) {
        if (nilaiUts >= 75) { // level 1
            if (nilaiUas >= 75) { // level 2
                if (kehadiran >= 80) { // level 3
                    if (tugas >= 80) { // level 4
                        return "Lulus dengan baik";
                    }
                }
            }
        }
        return "Tidak lulus"; 
    }
}