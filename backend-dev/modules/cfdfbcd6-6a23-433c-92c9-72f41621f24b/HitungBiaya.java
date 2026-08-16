/* Fungsi untuk menghitung biaya pengiriman berdasarkan jenis layanan (REG/EXP) dan status member (true/false). Layanan REG memiliki biaya 10.000, sedangkan EXP 20.000. Jika pelanggan berstatus member, maka diberikan diskon sebesar 10% dari biaya pengiriman. Hasil akhir berupa total biaya setelah diskon dalam bentuk desimal. */

public class HitungBiaya {
    public double hitungBiaya(String layanan, boolean member){
        double biaya = 0;
        double diskon = 0;

        switch (layanan) {
            case "REG": biaya = 10000; break;
            case "EXP": biaya = 20000; break;
        }
        if (member) {
            diskon = biaya * 0.1;
        } else {
            diskon = 0;
        }
        return biaya - diskon; 
    }
}