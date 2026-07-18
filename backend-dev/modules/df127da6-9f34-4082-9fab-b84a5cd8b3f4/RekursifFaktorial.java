public class RekursifFaktorial {

    public int rekursifFaktorial(int n) {
        if (n <= 1) {
            return 1;
        }

        return n * rekursifFaktorial(n - 1);
    }
}