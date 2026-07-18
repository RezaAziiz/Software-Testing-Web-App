public class SwitchWhile {

    public int switchWhile(int pilihan, int batas) {
        int total = 0;

        switch (pilihan) {

            case 1:
                int i = 1;
                while (i <= batas) {
                    total += i;
                    i++;
                }
                break;

            case 2:
                int j = 1;
                while (j <= batas) {
                    total += j * 2;
                    j++;
                }
                break;

            default:
                total = -1;
                break;
        }

        return total;
    }
}