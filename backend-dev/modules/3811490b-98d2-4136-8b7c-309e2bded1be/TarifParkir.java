public class TarifParkir {
    /*
     * DESKRIPSI:
     * Menghitung biaya parkir berdasarkan jenis kendaraan
     * dan lama parkir.
     * Setiap kendaraan memiliki tarif dasar untuk 2 jam pertama.
     * Jika lama parkir melebihi 2 jam, dikenakan biaya tambahan
     * untuk setiap jam berikutnya.
     */
    public int hitungTarif(String jenisKendaraan, int lamaParkir) {

        int tarif = 0;

        switch (jenisKendaraan) {

            case "Motor":
                tarif = 3000;
                if (lamaParkir > 2) {
                    tarif += (lamaParkir - 2) * 1000;
                }
                break;

            case "Mobil":
                tarif = 5000;
                if (lamaParkir > 2) {
                    tarif += (lamaParkir - 2) * 2000;
                }
                break;

            case "Bus":
                tarif = 10000;
                if (lamaParkir > 2) {
                    tarif += (lamaParkir - 2) * 3000;
                }
                break;

            default:
                tarif = 0;
                break;
        }

        return tarif;
    }
}