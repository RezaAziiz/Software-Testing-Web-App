public class IfWhile {
    public int ifWhile(int n) {
        int total = 0;

        if (n > 0) {
            int i = 1;

            while (i <= n) {
                total += i;
                i++;
            }
        }

        return total;
    }
}
