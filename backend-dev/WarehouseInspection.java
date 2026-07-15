/**
 * Memeriksa rak penyimpanan di gudang.
 *
 * Setiap baris rak diperiksa satu per satu (while),
 * sedangkan setiap kolom pada baris tersebut diperiksa menggunakan for.
 *
 * Jika ditemukan kode barang prioritas (targetCode),
 * pemeriksaan langsung dilanjutkan ke baris rak berikutnya.
 *
 * Jika ditemukan kombinasi posisi yang menunjukkan kondisi darurat
 * (i * j == 99), proses inspeksi dihentikan dan jumlah item
 * yang telah diperiksa dikembalikan.
 */
public class WarehouseInspection {
    public int inspectWarehouse(int totalRows, int totalColumns, int targetCode) {

        int inspectedItems = 0;
        int row = 0;
        OUTER_WHILE: while (row < totalRows) {

            for (int column = 0; column < totalColumns; column++) {
                if (row + column == targetCode) {
                    row++;
                    continue OUTER_WHILE;
                }
                if (row * column == 99) {
                    return inspectedItems;
                }
                inspectedItems++;
            }
            row++;
        }
        return inspectedItems;
    }
}