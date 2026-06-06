public class CekTahunKabisat {
    
    public boolean isYearKabisat(int idxMonth, int year) {
        boolean isKabisat;
        
        isKabisat = ((year % 4 == 0) && (year % 100 > 0)) || (year % 400 == 0); 
        return isKabisat;
    }
    
}