public class SeleksiPeserta {

    public String cekStatus(
            int usia,
            double nilai,
            String statusPendaftaran,
            String nomorPeserta) {

        if (usia < 17 || usia > 30) {
            return "Tidak memenuhi syarat umur";
        }

        if (nilai < 0.0 || nilai > 4.0) {
            return "IPK tidak valid";
        }

        if (!statusPendaftaran.equals("Aktif")) {
            return "Mahasiswa harus berstatus aktif";
        }

        if (nomorPeserta.length() != 9) {
            return "Kode mahasiswa tidak valid";
        }

        if (nilai >= 3.50) {
            return "Layak Beasiswa Prestasi";
        }

        if (nilai >= 3.00) {
            return "Layak Dipertimbangkan";
        }

        return "Belum Layak Beasiswa";
    }
}