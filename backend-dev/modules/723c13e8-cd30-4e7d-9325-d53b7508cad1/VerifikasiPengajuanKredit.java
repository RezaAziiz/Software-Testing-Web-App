/* Deskripsi:
 * Menghitung total skor kelayakan pengajuan kredit.
 * Skor hanya dihitung apabila seluruh tahapan verifikasi berhasil.
 */
public class VerifikasiPengajuanKredit {

    public int hitungSkorKredit(int skorIdentitas,
                                int skorPenghasilan,
                                int skorRiwayatKredit,
                                int skorJaminan,
                                int skorDokumen,
                                int skorWawancara) {
        int totalSkor = 0;

        if (skorIdentitas > 0) {                 // Level 1
            if (skorPenghasilan > 0) {           // Level 2
                if (skorRiwayatKredit > 0) {     // Level 3
                    if (skorJaminan > 0) {       // Level 4
                        if (skorDokumen > 0) {   // Level 5
                            if (skorWawancara > 0) { // Level 6
                                totalSkor = skorIdentitas
                                          + skorPenghasilan
                                          + skorRiwayatKredit
                                          + skorJaminan
                                          + skorDokumen
                                          + skorWawancara;
                            }
                        }
                    }
                }
            }
        }

        return totalSkor;
    }
}