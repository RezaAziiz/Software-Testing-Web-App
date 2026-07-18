public class IfElseDoWhile {
    public int ifElseDoWhile(int n, boolean kaliDua) {
        int total = 0;

        if (kaliDua) {
            int i = 1;

            do {
                total += i * 2;
                i++;
            } while (i <= n);
            
        } else {
            int i = 1;

            do {
                total += i;
                i++;
            } while (i <= n);
        }

        return total;
    }
}
