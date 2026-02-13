public class Pangkat{
	public float fungsiPangkatDua(int bil, int pangkat) {
		float result = 1;
		int temp, i;
		
		if (bil==0 && pangkat>0) {
			result = 0;
		}else if (pangkat>0) {
			i = 0;
			do {
				result = result * bil;
				i = i+1;
			}
			while (i<pangkat);
		}else if(pangkat<0){
			if(bil!=0){
				i = 0;
				while (i<pangkat) {
					result = result * 1/bil;
					i = i+1;
				}
			}else{
				result = -99999;
			}
		}else{ // pangkat = 0
			if(bil==0){
				result = -99999;
			}
		}
		return result;
	}
}
