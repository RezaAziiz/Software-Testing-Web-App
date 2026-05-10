public class HitungTotal {
    public int hitungTotal(int n) {
        int total = 0;
        int i = 1;

        while (i <= n) {
            total += i;
            i++;
        }

        return total;
    }
}