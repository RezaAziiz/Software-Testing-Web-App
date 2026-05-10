public class KomputasiRelasional {

    public boolean evaluasiSemuaKondisi(int angka1, int angka2, char huruf1, char huruf2, String teks) {
        // 1. Ekspresi relasional perbandingan numerik
        boolean cekLebihBesar = angka1 > angka2;
        boolean cekLebihKecil = angka1 < 100;
        boolean cekLebihBesarSama = angka2 >= 50;
        boolean cekLebihKecilSama = angka1 <= 10;
        
        // 2. Ekspresi relasional kesamaan/ketidaksamaan numerik
        boolean cekSamaNumerik = angka1 == angka2;
        boolean cekBedaNumerik = angka2 != 0;

        // 3. Ekspresi relasional kesamaan/ketidaksamaan karakter dan string
        boolean cekSamaKarakter = huruf1 == huruf2;
        boolean cekBedaString = teks != "Proses";

        // 4. Menggabungkan semua hasil (sequence murni, eksekusi dari atas ke bawah)
        // Sebuah variabel boolean akhir menampung satu kondisi gabungan
        boolean hasilAkhir = cekLebihBesar && cekLebihKecil && cekLebihBesarSama && 
                             cekLebihKecilSama && cekSamaNumerik && cekBedaNumerik && 
                             cekSamaKarakter && cekBedaString;

        return hasilAkhir;
    }
}