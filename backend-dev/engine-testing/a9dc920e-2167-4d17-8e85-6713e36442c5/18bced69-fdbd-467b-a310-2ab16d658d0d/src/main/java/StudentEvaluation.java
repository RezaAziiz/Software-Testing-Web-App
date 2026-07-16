public class StudentEvaluation {

    public String evaluateStudents(String[] names, int[] scores) {

        int passed = 0;
        for (int score : scores) {
            if (score >= 75) {
                passed++;
            }
        }
        if (passed == scores.length) {
            return "Semua siswa lulus";
        } else if (passed == 0) {
            return "Tidak ada siswa yang lulus";
        }
        for (String name : names) {
            if (name == null || name.isBlank()) {
                return "Data nama tidak valid";
            }
        }
        return "Sebagian siswa lulus";
    }
}