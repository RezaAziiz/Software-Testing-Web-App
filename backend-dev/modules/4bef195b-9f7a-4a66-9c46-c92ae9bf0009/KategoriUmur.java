/* Program: Kategori Umur
 * Deskripsi: Mengkategorikan umur menjadi anak-anak, remaja, atau dewasa
 * Tingkat Kesulitan: Mudah
 * Tipe Return: String
 * Parameter: int
 */

public class KategoriUmur {
    public String kategoriUmur(int umur) {
        String kategori;
        if (umur < 12) {
            kategori = "Anak-anak";
        } else if (umur < 18) {
            kategori = "Remaja";
        } else {
            kategori = "Dewasa";
        }
        return kategori;
    }
}