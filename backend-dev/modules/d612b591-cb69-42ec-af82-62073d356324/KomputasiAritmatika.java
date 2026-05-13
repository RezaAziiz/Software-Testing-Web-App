public class KomputasiAritmatika {

    public int hitungNilaiEkspresi(int x, int y, int z) {
        // 1. Deklarasi dan inisialisasi awal
        int hasilAkhir = 0;
        
        // 2. Ekspresi menggunakan +, -, *, dan kurung ()
        int langkah1 = (x + y) * (z - x);
        
        // 3. Ekspresi menggunakan modulus % dan pembagian /
        // (Dalam integer arithmetic, hasil pembagian akan otomatis dibulatkan ke bawah)
        int langkah2 = (langkah1 % 5) + (x / y);
        
        // 4. Penggabungan operator kompleks dalam satu baris
        int langkah3 = ((langkah1 - langkah2) * 2) / ((z % 3) + 1);
        
        // 5. Finalisasi perhitungan
        hasilAkhir = langkah3 + (x * 10) - (y % 2);
        
        return hasilAkhir;
    }
}