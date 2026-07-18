public class SwitchFor {

    public int switchFor(int pilihan, int batas) {
        int total = 0;

        switch (pilihan) {

            case 1:
                for (int i = 1; i <= batas; i++) {
                    total += i;
                }
                break;

            case 2:
                for (int i = 1; i <= batas; i++) {
                    total += i * 2;
                }
                break;

            default:
                total = -1;
                break;
        }

        return total;
    }
}
