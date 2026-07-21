public class GetSizeKaos {

	public char getSizeKaos_12(int T, int BB){
		char size = ' ';

		if (T > 170) {
			if ( (BB > 60) && (BB <= 80) ) {
				size = 'X';
			}
		}else { 
		     if (T > 150) {
		    	 if (BB <= 80) {
		    		 size = 'L';
		    	 }
		     }else{ 
		    	 size = 'M';
		     }
		}

		return size;
	}
}