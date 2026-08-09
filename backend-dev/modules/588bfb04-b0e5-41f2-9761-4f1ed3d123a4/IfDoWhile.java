public class IfDoWhile {
    public int ifDoWhile(int n) {
        int total = 0;

        if (n > 0) {
            int i = 1;

            do {
                total += i;
                i++;
            } while (i <= n);
        }

        return total;
    }
}
