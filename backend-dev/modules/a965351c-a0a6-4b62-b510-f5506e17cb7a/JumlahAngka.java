public class JumlahAngka {
    public int jumlahAngka(int n) {
        int total = 0;
        
        for (int i = 0; i <= n; i++) {
            total += i;
        }

        return total;
    }
}
