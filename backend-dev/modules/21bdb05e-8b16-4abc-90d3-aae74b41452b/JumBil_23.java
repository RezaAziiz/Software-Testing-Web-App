public class JumBil_23 {
    public int jumBil_23(int N){
		int sum, i;
		
		sum = 0;
		i = 0;
		do{
			sum = sum + i;
			i = i + 1;
		}while (i<N);
		return sum;
	}
}
