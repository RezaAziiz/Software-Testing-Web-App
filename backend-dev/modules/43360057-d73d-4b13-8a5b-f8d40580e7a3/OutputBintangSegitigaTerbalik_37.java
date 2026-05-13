public class OutputBintangSegitigaTerbalik_37 {

    public void outputBintangSegitigaTerbalik(int N) {
        int i, j;

        i = 1;
        while (i <= N) {
            j = 1;

            while (j < i) {
                System.out.print(" ");
                j = j + 1;
            }

            while (j <= N) {
                System.out.print("*");
                j = j + 1;
            }

            System.out.println();
            i = i + 1;
        }
    }
}