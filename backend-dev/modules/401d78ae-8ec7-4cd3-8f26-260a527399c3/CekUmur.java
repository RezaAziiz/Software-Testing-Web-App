public class CekUmur {

    public String tentukanKategoriUmur(int umur) {
        String kategori;

        // Struktur Selection: IF then - 1 kali else if - EndIF (else)
        if (umur < 18) {
            kategori = "Belum Dewasa (Anak-anak/Remaja)";
        } else if (umur <= 59) {
            kategori = "Dewasa";
        } else {
            // EndIF (Kondisi sisanya, yaitu umur >= 60)
            kategori = "Lansia";
        }

        return kategori;
    }
}