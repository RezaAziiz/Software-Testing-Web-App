public class ScoreAnalyzerLevelTwo {

    public String analyzeScores(int[] scores, int passingScore) {

        int passed = 0;
        for (int score : scores) {
            if (score == 999) {
                break;
            }
            if (score < 0) {
                continue;
            }
            if (score >= passingScore) {
                passed++;
            }
        }
        if (passed == 0) {
            return "Tidak Ada yang Lulus";
        } else if (passed == scores.length) {
            return "Semua Lulus";
        }
        return "Sebagian Lulus";
    }
}