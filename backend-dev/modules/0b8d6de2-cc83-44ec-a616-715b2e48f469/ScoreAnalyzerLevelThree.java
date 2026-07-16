public class ScoreAnalyzerLevelThree {

    public String analyzeScores(int[][] classes, int passingScore) {

        int passed = 0;
        OUTER: for (int[] classroom : classes) {
            for (int score : classroom) {
                if (score == 999) {
                    break OUTER;
                }
                if (score < 0) {
                    continue;
                }
                if (score == 100) {
                    continue OUTER;
                }
                if (score >= passingScore) {
                    passed++;
                }
            }
        }
        if (passed == 0) {
            return "Tidak Ada yang Lulus";
        } else if (passed >= 10) {
            return "Banyak Siswa Lulus";
        }
        return "Sebagian Siswa Lulus";
    }
}