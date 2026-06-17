/* Program: DecimalToRoman
 * Deskripsi: Mengonversi angka desimal ke angka Romawi
 * Nama: Muhammad Saiful Islam/141524020
 * Tanggal/versi: 22 November 2015/v.0
 */

public class DecimalToRoman {
    public String decimalToRoman (int bilangan) {
        String roman = "";
        int i;
        for (i = 0; i < bilangan / 1000; i++) {
            roman += "M";
        }
        bilangan = bilangan % 1000;

        if (bilangan >= 900) {
            roman += "CM";
            bilangan -= 900;
        } else if (bilangan >= 500) {
            roman += "D";
            bilangan -= 500;
        } else if (bilangan >= 400) {
            roman += "CD";
            bilangan -= 400;
        }
        for (i = 0; i < bilangan / 100; i++) {
            roman += "C";
        }
        bilangan = bilangan % 100;

        if (bilangan >= 90) {
            roman += "XC";
            bilangan -= 90;
        } else if (bilangan >= 50) {
            roman += "L";
            bilangan -= 50;
        } else if (bilangan >= 40) {
            roman += "XL";
            bilangan -= 40;
        }
        for (i = 0; i < bilangan / 10; i++) {
            roman += "X";
        }
        bilangan = bilangan % 10;

        if (bilangan >= 9) {
            roman += "IX";
            bilangan -= 9;
        } else if (bilangan >= 5) {
            roman += "V";
            bilangan -= 5;
        } else if (bilangan >= 4) {
            roman += "IV";
            bilangan -= 4;
        }
        for (i = 0; i < bilangan; i++) {
            roman += "I";
        }

        return roman;
    }
} 
