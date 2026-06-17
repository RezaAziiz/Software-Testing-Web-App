public class HitungJumlahPerkalian {
    public static int hitungJumlahPerkalian(int n) {
        int total = 0;

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                total += i * j;
            }
        }

        return total;
    }
}
