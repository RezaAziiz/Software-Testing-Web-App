public class CariTarget {

    public int cariTarget(int batas, int target) {

        int ditemukan = -1;
        SEARCH: for (int i = 0; i < batas; i++) {
            if (i == target) {
                ditemukan = i;
                break SEARCH;
            }
        }
        return ditemukan;
    }
}