public class CekNilai {

    public String cekKelulusan(int nilai) {
        int batasLulus = 70;
        int nilaiTambahan = 5;

        if (nilai >= batasLulus) {
            nilai = nilai + nilaiTambahan;
            String status = "Lulus";
            return status;
        }

        nilai = nilai + nilaiTambahan;
        String status = "Tidak Lulus";
        return status;
    }
}