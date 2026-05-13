public class NestedIfDua {
    public void nestedIfDua(int nilai, int kehadiran) {
        if (nilai >= 75) { // level 1
            if (kehadiran >= 80) { // level 2
                System.out.println("Lulus");
            }
        }
    }
}