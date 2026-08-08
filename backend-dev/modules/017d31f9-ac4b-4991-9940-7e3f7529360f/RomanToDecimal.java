public class RomanToDecimal {
    public int romanToDecimal(String roman) {
        int decimal = 0;
        int lastNumber = 0;
        for (int i = roman.length() - 1; i >= 0; i--) {
            char romanChar = roman.charAt(i);
 	    int number = 0;
            switch (romanChar) {
                case 'I' : number = 1; break;
                case 'V' : number = 5; break;
                case 'X' : number = 10; break;
                case 'L' : number = 50; break;
                case 'C' : number = 100; break;
                case 'D' : number = 500; break;
                case 'M' : number = 1000; break;
                default : throw new IllegalArgumentException("Karakter Romawi tidak valid: " + romanChar);
            };
            if (number < lastNumber) {
                decimal -= number;
            } else {
                // Jika tidak, tambahkan ke total
                decimal += number;
            }
            lastNumber = number;
        }

        return decimal;
    }
}
