public class SelisihTanggal {
    public int selisihTanggal(int tanggalFrom, int bulanFrom, int tahunFrom, int tanggalTo, int bulanTo, int tahunTo) {
        int[] hariBulan = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

        int selisihHari = 0;
        
        if (tahunFrom == tahunTo) {
            if (bulanFrom == bulanTo) {
                selisihHari = tanggalTo - tanggalFrom;
            } else {
                // Handling leap year for February
                if ((tahunTo % 4 == 0 && tahunTo % 100 != 0) || tahunTo % 400 == 0) {
                    hariBulan[1] = 29; // Set February to 29 days for leap year
                }
                selisihHari += hariBulan[bulanFrom - 1] - tanggalFrom;
                for (int i = bulanFrom; i < bulanTo - 1; i++) {
                    selisihHari += hariBulan[i];
                }
                selisihHari += tanggalTo;
            }
        } else {
            selisihHari += hariBulan[bulanFrom - 1] - tanggalFrom;
            for (int i = bulanFrom; i < 12; i++) {
                // Handling leap year for February in the initial year
                if (i == 1 && ((tahunFrom % 4 == 0 && tahunFrom % 100 != 0) || tahunFrom % 400 == 0)) {
                    selisihHari += 1; // Add one day for leap year February
                }
                selisihHari += hariBulan[i];
            }
            for (int i = tahunFrom + 1; i < tahunTo; i++) {
                // Adding days for each year between from and to (handling leap years)
                if ((i % 4 == 0 && i % 100 != 0) || i % 400 == 0) {
                    selisihHari += 366; // Leap year has 366 days
                } else {
                    selisihHari += 365; // Normal year has 365 days
                }
            }
            for (int i = 0; i < bulanTo - 1; i++) {
                // Handling leap year for February in the final year
                if (i == 1 && ((tahunTo % 4 == 0 && tahunTo % 100 != 0) || tahunTo % 400 == 0)) {
                    selisihHari += 1; // Add one day for leap year February
                }
                selisihHari += hariBulan[i];
            }
            selisihHari += tanggalTo;
        }

        return selisihHari;
    }
}