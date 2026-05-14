public class ProsesTransaksi {

    public String evaluasi(int totalBelanja, String metodeBayar, String kodePromo) {
        String hasil = "GAGAL";

        // KASUS 1: Jebakan Teks (String Literal Trap)
        // Algoritma akan mengira teks di bawah ini adalah blok kode beneran!
        String logPesan = "Sistem mengecek if ( totalBelanja > 0 ) { lanjut } else { batal }";

        // KASUS 2: Nested IF dalam satu baris (One-liner Nested IF)
        if(totalBelanja>50000) if(metodeBayar.equals("CASH")) hasil = "BERHASIL_CASH";

        // KASUS 3: Format 'else if' patah yang merusak baris
        if (kodePromo.length() == 5) {
            hasil = hasil + "_PROMO_VALID";
        } else
        if (kodePromo.length() == 4) {
            hasil = hasil + "_PROMO_MEMBER";
        }
        else hasil = hasil + "_TANPA_PROMO";

        // KASUS 4: Loop tanpa kurung kurawal (Menyebabkan Stack Leak di Python)
        int counter = 0;
        while (counter < 3) 
            counter++;

        return hasil;
    }
}