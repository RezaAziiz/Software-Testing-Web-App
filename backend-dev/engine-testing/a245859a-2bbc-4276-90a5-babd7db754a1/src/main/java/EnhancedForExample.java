public class EnhancedForExample {

    public String analyzeScores(int[] scores) {
        int passed = 0;

        for (int score : scores) {
            if (score >= 75) {
                passed++;
            }
        }
        if (passed == scores.length) {
            return "Semua Lulus";
        } else if (passed == 0) {
            return "Tidak Ada yang Lulus";
        }
        return "Sebagian Lulus";
    }
}