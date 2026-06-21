public class JumBilDoWhile {

    public int jumBil_23(int N){
        int sum, i;
        
        sum = 0;
        i = 0;
        do{
            sum = sum + 1;
            i = i + 1;
        }while (i<=N);
        
        return sum;
    }
}