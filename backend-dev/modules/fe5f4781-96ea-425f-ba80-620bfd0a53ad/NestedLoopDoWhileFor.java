public class NestedLoopDoWhileFor {
    public void nestedLoopDoWhileFor(int batas) {
        int i = 1;

        do {
            System.out.println("Perulangan ke-" + i);

            for (int j = 1; j <= 3; j++) {
                System.out.println("  Nilai j = " + j);
            }

            i++;
        } while (i <= batas);
    }
}