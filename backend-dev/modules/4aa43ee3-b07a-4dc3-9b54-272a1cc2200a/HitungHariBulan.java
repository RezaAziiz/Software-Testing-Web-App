public class HitungHariBulan {

    public int getNumberDayMonth_18(int idxMonth, int year) {
        int numDays = 0;
        
        switch (idxMonth) {
            case 1: 
            case 3: 
            case 5:
            case 7: 
            case 8: 
            case 10:
            case 12:
                numDays = 31;
                break;
            case 4: 
            case 6:
            case 9: 
            case 11:
                numDays = 30;
                break;
            case 2:
                if (((year % 4 == 0) && !(year % 100 == 0)) || (year % 400 == 0))
                    numDays = 29;
                else
                    numDays = 28;
                break;
            default:
                numDays = 0;
                break;
        }
        
        return numDays;
    }
    
}