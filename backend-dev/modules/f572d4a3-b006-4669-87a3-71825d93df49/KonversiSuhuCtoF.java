/* Program: Konversi Celcius To Fahrenheit 
 * Deskripsi: Mengonversi suhu dalam Celcius ke Fahrenheit
 * Author : Muhammad Saiful Islam
 * Tanggal/versi: 2 November 2015/v1.0
 * Formula: °F = °C × 1,8 + 32
 */

 public class KonversiSuhuCtoF {
    public float konversiCelciustoFahrenheit (float celcius){
        float fahrenheit;

        fahrenheit = (float) (celcius * 1.8 + 32);
        return  fahrenheit;
    }
}

