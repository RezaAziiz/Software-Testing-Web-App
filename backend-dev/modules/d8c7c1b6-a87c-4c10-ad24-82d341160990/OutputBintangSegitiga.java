public class OutputBintangSegitiga {
    public void outputBintangSegitiga(int N){
		int i, j;
		
		i = 1;
		while (i<=N){
			for (j=1; j<=i; j++) {
				System.out.print("*");
			}
			System.out.println();
			i = i+1;
		}
	}
}
