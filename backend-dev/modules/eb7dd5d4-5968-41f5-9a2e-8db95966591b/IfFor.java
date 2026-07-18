public class IfFor {
    public int ifFor(int n) {
        int total = 0;

        if (n > 0) {
            for (int i = 1; i <= n; i++) {
                total += i;
            }
        }

        return total;
    }
}
