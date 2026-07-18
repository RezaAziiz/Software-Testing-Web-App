public class BagiBilangan {

    public int bagiBilangan(int pembilang, int penyebut) {
        int hasil = 0;

        try {
            hasil = pembilang / penyebut;
        } catch (ArithmeticException e) {
            hasil = -1;
        }

        return hasil;
    }
}
