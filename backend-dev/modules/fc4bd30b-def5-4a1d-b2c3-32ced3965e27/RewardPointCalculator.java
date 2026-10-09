public class RewardPointCalculator {

    public int calculatePoints(int memberType, int totalPurchase) {
        int points = 0;

        switch (memberType) {

            case 1:
                if (totalPurchase >= 100) {
                    points = 20;
                } else {
                    points = 10;
                }
                break;

            case 2:
                if (totalPurchase >= 100) {
                    points = 30;
                } else {
                    points = 15;
                }
                break;

            default:
                points = -1;
                break;
        }

        return points;
    }
}