public class PromoBelanja {

    public String tentukanPromo(int n) {
        String daftarPromo = "";

        // 1 Loop utama untuk membaca pesanan dari 1 sampai n
        for (int i = 1; i <= n; i++) {

            // Branching Tingkat 1: Cek VIP (Genap) atau Reguler (Ganjil)
            if (i % 2 == 0) {
                // Nested Branching 1: Evaluasi promo VIP
                if (i % 4 == 0) {
                    daftarPromo += "Order " + i + ": VIP - Diskon 50%\n";
                } else {
                    daftarPromo += "Order " + i + ": VIP - Diskon 20%\n";
                }
            } else {
                // Nested Branching 2: Evaluasi promo Reguler
                if (i % 3 == 0) {
                    daftarPromo += "Order " + i + ": Reguler - Cashback 10%\n";
                } else {
                    daftarPromo += "Order " + i + ": Reguler - Tanpa Promo\n";
                }
            }
        }

        return daftarPromo;
    }
}