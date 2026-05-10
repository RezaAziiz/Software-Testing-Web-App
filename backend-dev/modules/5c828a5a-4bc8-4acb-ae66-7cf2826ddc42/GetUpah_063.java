public class GetUpah_063 {
    public int getUpah_063(int jamMasuk, int jamKeluar){
		int lama, biaya;
		
		if (jamKeluar > jamMasuk) {
			lama = jamKeluar - jamMasuk;
		}else if (jamMasuk > jamKeluar) {
			lama = 12 - jamMasuk + jamKeluar;
		}else{
			lama = 0;
		} 
		if (lama <= 2) {
			biaya = 2000;
		}else {
			biaya = 2000 + ((lama-2) * 500);
		}
		return biaya;
	}
}