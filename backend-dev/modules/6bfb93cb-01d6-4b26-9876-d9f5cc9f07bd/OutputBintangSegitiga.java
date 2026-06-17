public class OutputBintangSegitiga {
    public String outputBintangSegitiga(int N){
		String result = "";
		int i, j;
		
		i = 1;
		while (i<=N){
			for (j=1; j<=i; j++) {
				result += "*";
			}
			result += "\n";
			i = i+1;
		}
		return result;
	}
}
