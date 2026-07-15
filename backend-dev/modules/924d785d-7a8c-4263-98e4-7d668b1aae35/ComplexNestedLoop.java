/**
 * Deskripsi :
 * Melakukan analisis terhadap kombinasi lima buah perulangan bersarang
 * berdasarkan nilai parameter limit. Parameter limit menentukan jumlah
 * iterasi pada setiap tingkat perulangan, sehingga semakin besar nilainya
 * maka semakin banyak kombinasi yang akan diproses. Selama proses iterasi,
 * program melakukan berbagai validasi menggunakan percabangan bertingkat,
 * serta memanfaatkan mekanisme return, break, dan continue untuk
 * mengendalikan alur eksekusi. Hasil akhir berupa string "MATCH",
 * "POSITIVE", atau "NEGATIVE" yang ditentukan berdasarkan nilai score
 * yang diperoleh selama proses analisis.
 */
public class ComplexNestedLoop {

    public String analyze(int limit) {

        int score = 0;

        for (int a = 0; a < limit; a++) {

            for (int b = 0; b < limit; b++) {

                for (int c = 0; c < limit; c++) {

                    for (int d = 0; d < limit; d++) {

                        for (int e = 0; e < limit; e++) {

                            if (a == b) {

                                if (c == d) {

                                    score++;

                                    if (score > 5) {
                                        return "MATCH";
                                    }

                                } else {

                                    if (e % 2 == 0) {
                                        continue;
                                    }

                                }

                            } else {

                                if (a + b > c + d) {

                                    score += 2;

                                    if (score > 10) {
                                        break;
                                    }

                                } else if (e > 2) {

                                    score--;

                                } else {

                                    score += 3;

                                }
                            }

                        }
                    }
                }
            }
        }

        if (score > 0) {
            return "POSITIVE";
        }

        return "NEGATIVE";
    }
}