public class DeretGanjilGenap {

    public String OutputDeretGanjilGenap_27(int N) {
        int i, nGanjil, nGenap;
        int[] deretGanjil = new int[N];
        int[] deretGenap = new int[N];
        StringBuilder output = new StringBuilder();
        nGanjil = 0;
        nGenap = 0;

        for (i = 1; i <= N; i++) {
            if (i % 2 > 0) {
                deretGanjil[nGanjil] = i;
                nGanjil = nGanjil + 1;
            } else {
                deretGenap[nGenap] = i;
                nGenap = nGenap + 1;
            }
        }
        output.append("Deret Ganjil\n");
        for (i = 0; i < nGanjil; i++) {
            output.append(deretGanjil[i]).append(" ");
        }
        output.append("\nDeret Genap\n");
        for (i = 0; i < nGenap; i++) {
            output.append(deretGenap[i]).append(" ");
        }
        return output.toString();
    }
}