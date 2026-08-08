public class KelayakanBeasiswa {

    public String cekKelayakan(
            int umur,
            double ipk,
            String statusMahasiswa,
            String kodeMahasiswa) {
        if (umur < 17 || umur > 30) {
            return "Tidak memenuhi syarat umur";
        }
        if (ipk < 0.0 || ipk > 4.0) {
            return "IPK tidak valid";
        }
        if (!statusMahasiswa.equals("Aktif")) {
            return "Mahasiswa harus berstatus aktif";
        }
        if (kodeMahasiswa.length() != 9) {
            return "Kode mahasiswa tidak valid";
        }
        if (ipk >= 3.50) {
            return "Layak Beasiswa Prestasi";
        }
        if (ipk >= 3.00) {
            return "Layak Dipertimbangkan";
        }
        return "Belum Layak Beasiswa";
    }
}