public class SwitchDoWhile {

    public int switchDoWhile(int pilihan, int batas) {
        int total = 0;

        switch (pilihan) {

            case 1:
                int i = 1;
                do {
                    total += i;
                    i++;
                } while (i <= batas);
                break;

            case 2:
                int j = 1;
                do {
                    total += j * 2;
                    j++;
                } while (j <= batas);
                break;

            default:
                total = -1;
                break;
        }

        return total;
    }
}