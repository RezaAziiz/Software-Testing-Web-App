/* Program: Mengeja Nominal Ke Dalam Huruf
 * Deskripsi: Melakukan pengejaan dari sebuah bilangan
 * Author: Najib Alimudin Fajri/221524053
 * Tanggal/versi: 21 Juni 2024/v.0
 */

public class EjaNominal {
    public String ejaNominal(int bilangan) {
        String[] huruf = {"", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan"};
        String[] units = {"juta", "ribu", ""};
        int[] divisors = {1000000, 1000, 1};

        String hasil = "";
        for (int i = 0; i < units.length; i++) {
            int segment = bilangan / divisors[i];
            if (segment > 0) {
                int ratusan = segment / 100;
                int puluhan = (segment % 100) / 10;
                int satuan = segment % 10;

                if (ratusan > 0) {
                    hasil += (ratusan == 1 ? "seratus" : huruf[ratusan] + " ratus") + " ";
                }

                if (puluhan > 0) {
                    if (puluhan == 1) {
                        if (satuan == 0) {
                            hasil += "sepuluh ";
                        } else if (satuan == 1) {
                            hasil += "sebelas ";
                        } else {
                            hasil += huruf[satuan] + " belas ";
                        }
                    } else {
                        hasil += huruf[puluhan] + " puluh ";
                    }
                }

                if (puluhan != 1 && satuan > 0) {
                    hasil += huruf[satuan] + " ";
                }

                hasil += units[i] + " ";
            }
            bilangan %= divisors[i];
        }

        return hasil.trim();
    }
}
