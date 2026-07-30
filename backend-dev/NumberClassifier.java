public class NumberClassifier {

    public String classifyNumber(int number) {
        if (number > 0) {
            return "Positive";
        } else if (number < 0) {
            return "Negative";
        }
        return "Zero";
    }
}