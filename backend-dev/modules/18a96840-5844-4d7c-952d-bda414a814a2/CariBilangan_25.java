public class CariBilangan_25 {

    public boolean cariBil(int bil[], int N, int cari) {
        int i;
        boolean ketemu = false;

        i = 0;
        while (i < N && ketemu == false) {
            if (bil[i] == cari) {
                ketemu = true;
            }
            i = i + 1;
        }

        return ketemu;
    }
}