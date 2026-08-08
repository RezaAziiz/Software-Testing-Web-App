public class IfElseFor {
    public int ifElseFor(int n, boolean genap) {
        int total = 0;

        if (genap) {
            for (int i = 1; i <= n; i++) {
                if (i % 2 == 0) {
                    total += i;
                }
            }
        } else {
            for (int i = 1; i <= n; i++) {
                if (i % 2 != 0) {
                    total += i;
                }
            }
        }

        return total;
    }
}
