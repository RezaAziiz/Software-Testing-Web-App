public class LoanEligibility {

    public String evaluate(int age,
            int income,
            int creditScore,
            boolean hasDebt,
            boolean hasCollateral) {

        int score = 0;
        if (age >= 21) {
            score += 10;
        } else {
            score -= 20;
        }
        if (income >= 7000000) {
            if (creditScore >= 700) {
                score += 30;
            } else {
                score += 10;
            }
            if (!hasDebt) {
                score += 20;
            } else {
                score -= 10;
            }
        } else {
            if (creditScore >= 700) {
                score += 15;
            } else {
                score -= 15;
            }
            if (hasCollateral) {
                score += 25;
            } else {
                score -= 5;
            }
        }
        if (score >= 50) {
            return "APPROVED";
        } else {
            return "REJECTED";
        }
    }
}