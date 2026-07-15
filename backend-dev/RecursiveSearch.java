public class RecursiveSearch {

    public int search(int n) {
        if (n < 0) {
            return -1;
        }
        if (n == 0) {
            return 0;
        }
        return search(n - 1);
    }
}