public class RemedialEvaluation {

    public String evaluateClass(int[] scores, int passingScore) {

        int passed = 0;
        for (int score : scores) {
            if (score >= 0) {
                if (score >= passingScore) {
                    passed++;
                }
            }
        }
        if (passed == scores.length) {
            return "Tidak Perlu Remedial";
        } else if (passed == 0) {
            return "Seluruh Siswa Remedial";
        }

        return "Sebagian Siswa Remedial";
    }
}