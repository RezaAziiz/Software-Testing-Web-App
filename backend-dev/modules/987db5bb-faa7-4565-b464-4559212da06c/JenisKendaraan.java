public class JenisKendaraan {
    public String jenisKendaraan(int nomorKendaraan) {
        String kendaraan;

        switch (nomorKendaraan) {
            case 1:
                kendaraan = "Mobil";
                break;
            case 2:
                kendaraan = "Motor";
                break;
            case 3:
                kendaraan = "Sepeda";
                break;
            case 4:
                kendaraan = "Truk";
                break;
            default:
                kendaraan = "Jenis kendaraan tidak valid";
        }

        return kendaraan;
    }
}