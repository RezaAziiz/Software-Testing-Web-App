public class HitungSkorProyek {

    public int hitungSkorProyek(int jumlahProyek) {
        int totalSkor = 0;

        for (int proyek = 1; proyek <= jumlahProyek; proyek++) {
            int tahap = 1;

            while (tahap <= 2) {
                int reviewer = 1;

                do {
                    for (int aspek = 1; aspek <= 2; aspek++) {
                        totalSkor += proyek + tahap + reviewer + aspek;
                    }

                    reviewer++;

                } while (reviewer <= 2);

                tahap++;
            }
        }

        return totalSkor;
    }
}