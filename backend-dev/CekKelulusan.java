public class CekKelulusan {

    public String cekKelulusan(int nilai) {
        if (nilai >= 75) {
            return "Lulus";
        } else {
            return "Tidak Lulus";
        }
    }
}