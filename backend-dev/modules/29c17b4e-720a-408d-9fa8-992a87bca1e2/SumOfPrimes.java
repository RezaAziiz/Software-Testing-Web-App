public class SumOfPrimes {

    /**
     * Menghitung jumlah bilangan prima dari 1 sampai max (menggunakan labeled
     * continue)
     * 
     * @param max batas atas
     * @return total sum bilangan prima
     */
    public int sumOfPrimes(int max) {
        int total = 0;

        OUT: for (int i = 1; i <= max; ++i) {
            for (int j = 2; j < i; ++j) {
                if (i % j == 0) {
                    continue OUT;
                }
            }
            total += i;
        }

        return total;
    }
}