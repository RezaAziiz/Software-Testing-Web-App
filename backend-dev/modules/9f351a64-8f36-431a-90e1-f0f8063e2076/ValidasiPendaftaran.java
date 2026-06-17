public class ValidasiPendaftaran {

    public String prosesValidasi(int umur, int pengalamanKerja, boolean adaSertifikat, int nilaiTes) {
        String status;

        // Level Kedalaman 1
        if (umur >= 18) {

            // Level Kedalaman 2
            if (pengalamanKerja >= 2) {

                // Level Kedalaman 3
                if (adaSertifikat) {

                    // Level Kedalaman 4
                    if (nilaiTes >= 80) {
                        status = "Diterima: Jalur Profesional Tersertifikasi";
                    } else {
                        status = "Ditolak: Nilai tes di bawah standar profesional (Min 80)";
                    } // EndIF Level 4

                } else {
                    // Cabang Else Level 3
                    if (nilaiTes >= 90) {
                        status = "Diterima: Jalur Potensi Tinggi (Tanpa Sertifikat)";
                    } else {
                        status = "Ditolak: Tidak ada sertifikat dan nilai tes gagal mencapai batas khusus (Min 90)";
                    }
                } // EndIF Level 3

            } else {
                // Cabang Else Level 2
                if (nilaiTes >= 85) {
                    status = "Diterima: Jalur Junior Trainee";
                } else {
                    status = "Ditolak: Kurang pengalaman dan nilai tes tidak mencukupi untuk Trainee (Min 85)";
                }
            } // EndIF Level 2

        } else {
            // Cabang Else Level 1
            status = "Ditolak: Belum cukup umur (Min 18 tahun)";
        } // EndIF Level 1

        return status;
    }
}