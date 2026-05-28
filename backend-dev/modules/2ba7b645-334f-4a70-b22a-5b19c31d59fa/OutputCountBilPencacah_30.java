public class OutputCountBilPencacah_30 {

    public int[] hitungPencacah(int batasAkhir) {
        // Deklarasi variabel pencacah
        int hitungSisa0 = 0;
        int hitungSisa1 = 0;
        int hitungSisa2 = 0;

        // Struktur Looping: For
        for (int i = 1; i <= batasAkhir; i++) {
            
            // Struktur Selection di dalam blok For: Switch Case
            switch (i % 3) {
                case 0:
                    hitungSisa0 = hitungSisa0 + 1;
                    break;
                case 1:
                    hitungSisa1 = hitungSisa1 + 1;
                    break;
                case 2:
                    hitungSisa2 = hitungSisa2 + 1;
                    break;
                default:
                    break;
            } // End of Switch
            
        } // End of For Loop

        return new int[]{hitungSisa0, hitungSisa1, hitungSisa2};
    }

}