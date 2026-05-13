public class CekGrade {
    public String cekGrade(int nilai) {
        String grade;

        switch (nilai) {
            case 90:
                grade = "A";
                break;
            case 80:
                grade = "B";
                break;
            case 70:
                grade = "C";
                break;
            default:
                grade = "D";
                break;
        }

        return grade;
    }
}