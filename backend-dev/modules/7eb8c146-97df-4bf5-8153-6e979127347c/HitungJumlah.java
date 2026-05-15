public class HitungJumlah {
    public int hitungJumlah(int n) {
        int total = 0;

        for (int i = 1; i <= n; i++) {
            total += i;
        }

        return total;
    }
}