/* Program: Status Kendaraan
 * Deskripsi: Menentukan status kendaraan berdasarkan bahan bakar
 * Tingkat Kesulitan: Mudah
 * Tipe Return: String
 * Parameter: int (persentase bahan bakar)
 */

public class StatusKendaraan {
    public String statusKendaraan(int persenBahanBakar) {
        String status;
        if (persenBahanBakar >= 75) {
            status = "Penuh";
        } else if (persenBahanBakar >= 50) {
            status = "Banyak";
        } else if (persenBahanBakar >= 25) {
            status = "Sedang";
        } else if (persenBahanBakar > 0) {
            status = "Sedikit";
        } else {
            status = "Kosong";
        }
        return status;
    }
}