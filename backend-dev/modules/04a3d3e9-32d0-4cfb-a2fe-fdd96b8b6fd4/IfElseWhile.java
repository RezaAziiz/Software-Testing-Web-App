public class IfElseWhile {
    public int ifElseWhile(int n, boolean kaliDua) {
        int total = 0;

        if (kaliDua) {
            int i = 1;

            while (i <= n) {
                total += i * 2;
                i++;
            }
        } else {
            int i = 1;

            while (i <= n) {
                total += i;
                i++;
            }
        }

        return total;
    }
}
