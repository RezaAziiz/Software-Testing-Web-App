public class HitungHuruf {

    public int hitungHuruf(String teks) {
        int jumlah = 0;

        for (char c : teks.toCharArray()) {
            jumlah++;
        }

        return jumlah;
    }
}