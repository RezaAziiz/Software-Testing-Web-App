public class RewardPoint {
    public int calculateRewardPoints(
            int transactionCount,
            boolean premiumMember) {
        int totalPoints = 0;

        if (premiumMember) {
            int transaction = 1;
            do {
                totalPoints += transaction * 2;
                transaction++;
            } while (transaction <= transactionCount);
        } else {
            int transaction = 1;
            do {
                totalPoints += transaction;
                transaction++;
            } while (transaction <= transactionCount);
        }
        return totalPoints;
    }
}
