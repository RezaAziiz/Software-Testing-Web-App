/* DESKRIPSI:
 * Menentukan status kehadiran pegawai
 * berdasarkan jam kedatangan.
 */
public class StatusKehadiran {

    public String statusKehadiran(int jamMasuk) {

        if (jamMasuk <= 8) {
            return "Tepat Waktu";
        } else {
            return "Terlambat";
        }
    }
}