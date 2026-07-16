public class ScoreAnalyzerLevelOne {

    public String analyzeScores(int[] scores, int passingScore) {

        int passed = 0;
        for (int score : scores) {
            if (score < 0) {
                continue;
            }
            if (score >= passingScore) {
                passed++;
            }
        }
        if (passed == 0) {
            return "Tidak Ada yang Lulus";
        }
        return "Ada Siswa yang Lulus";
    }
}