public class NestedIf4x {
    public static void nestedIf4x(int nilai, int kehadiran, boolean tugasLengkap, boolean ikutUjian) {
        if (nilai >= 75) { // level 1
            if (kehadiran >= 80) { // level 2
                if (tugasLengkap) { // level 3
                    if (ikutUjian) { // level 4
                        System.out.println("Lulus dengan baik");
                    }
                }
            }
        }
    }
}
