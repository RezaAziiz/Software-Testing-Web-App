public class LevelTwoComplexity {
    public int processBasic(int limitX, int limitY, int targetCode) {
        int result = 0;
        int i = 0;
        // TINGKAT 1: while
        OUTER_WHILE: while (i < limitX) {
            // TINGKAT 2: for
            for (int j = 0; j < limitY; j++) {
                if (i + j == targetCode) {
                    i++;
                    // CFG harus menunjuk ke evaluasi kondisi (i < limitX)
                    continue OUTER_WHILE;
                }
                if (i * j == 99) {
                    // CFG harus langsung menuju node End (memotong 2 tingkat)
                    return result;
                }
                result += (i + j);
            }
            i++;
        }
        return result;
    }
}