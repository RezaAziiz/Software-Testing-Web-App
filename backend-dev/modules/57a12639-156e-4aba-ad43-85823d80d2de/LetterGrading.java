/* Program: Letter Grading */

public class LetterGrading {
    public String letterGrading(int score) {
        String grade = "";
        String result = "";
        
        if (score >= 0 && score <= 100) {
            if (score >= 90) {
                grade = "A";
            } else if (score >= 80 && score < 90) {
                grade = "B";
            } else if (score >= 70 && score < 80) {
                grade = "C";
            } else if (score >= 60 && score < 70) {
                grade = "D";
            } else {
                grade = "E";
            }

            switch (grade) {
                case "A": 
                    result = "Excellent";
                    break;
                case "B": 
                    result = "Very Good";
                    break;
                case "C": 
                    result = "Good";
                    break;
                case "D": 
                    result = "Above Average";
                    break;
                case "E": 
                    result = "Satisfactory";
                    break;
            }

        } else {
            result = "Invalid Score";
        }

        return result;
    }
}