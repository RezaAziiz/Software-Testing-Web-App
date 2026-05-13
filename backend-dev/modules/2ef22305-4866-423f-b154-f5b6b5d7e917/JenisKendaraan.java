public class JenisKendaraan {
    public String jenisKendaraan(int nomorKendaraan) {
        switch (nomorKendaraan) {
            case 1:
                return "Mobil";
            case 2:
                return "Motor";
            case 3:
                return "Sepeda";
            case 4:
                return "Truk";
            default:
                return "Jenis kendaraan tidak valid";
        }
    }
}