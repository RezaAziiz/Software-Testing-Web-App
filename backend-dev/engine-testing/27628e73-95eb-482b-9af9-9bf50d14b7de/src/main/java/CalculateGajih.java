public class CalculateGajih {

	public int calCulateGajih_17(char gol, int durasiJamKerja) {	
		int upah=0;
		switch (gol) {
			case 'A' : upah = durasiJamKerja * 10000;
				       if (durasiJamKerja > 40) {
				    	   upah = upah + (durasiJamKerja * 5000);
					   }
				       break;
			case 'B' : upah = durasiJamKerja * 7500;
					   if (durasiJamKerja > 40) {
						   upah = upah + (durasiJamKerja * 4000);
					   }
					   break;
			case 'C' : upah = durasiJamKerja * 5000;
					   if (durasiJamKerja > 40) {
						   upah = upah + (durasiJamKerja * 3000);
					   }
					   break;
			case 'D' : upah = durasiJamKerja * 2500;
					   if (durasiJamKerja > 40) {
						   upah = upah + (durasiJamKerja * 2000);
					   }
					   break;
			default : System.out.print("Golongan tidak ada"); break;
		}
		return upah;
	}
}