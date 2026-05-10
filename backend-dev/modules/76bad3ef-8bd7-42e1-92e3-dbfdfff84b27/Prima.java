public class Prima {
    public String prima(int bilangan) {
        // Bilangan kurang dari 2 bukan bilangan prima
        if (bilangan < 2) {
            return "bukan prima";
        }

        // Memeriksa bilangan dari 2 hingga akar kuadrat dari bilangan
        for (int i = 2; i <= Math.sqrt(bilangan); i++) {
            if (bilangan % i == 0) {
                return "bukan prima";
            }
        }

        return "prima";
    }
}
