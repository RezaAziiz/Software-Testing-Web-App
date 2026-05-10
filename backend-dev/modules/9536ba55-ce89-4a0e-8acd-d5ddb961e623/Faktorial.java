/* Program: Faktorial 
 * Deskripsi: Menghitung nilai faktorial
 * Author: Muhammad Imam Fauzan
 * Tanggal/versi: 6 Desember 2015 / 00
 */

 public class Faktorial {
    public int faktorial (int bilangan) {
        int i, hasilFaktorial = 1;

        for ( i = 1 ; i <= bilangan ; i++ )
            hasilFaktorial *= i;

        return hasilFaktorial;
    }
}
