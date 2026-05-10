public class NestedIf3x {
    public static void nestedIf3x(int nilaiUts, int nilaiUas, int kehadiran, int tugas) {
        if (nilaiUts >= 75) { // level 1
            if (nilaiUas >= 75) { // level 2
                if (tugas >= 80) { // level 3
                    System.out.println("Lulus dengan baik");
                }
            }
        }
    }
}
