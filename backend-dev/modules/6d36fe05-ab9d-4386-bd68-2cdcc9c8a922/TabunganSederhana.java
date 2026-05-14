public class TabunganSederhana {

    public int hitungSaldoAkhir(int saldoAwal, int setor, int tarik) {
        int saldoAkhir;
        
        // Komputasi urut (sequence) murni menggunakan operator + dan -
        saldoAkhir = saldoAwal + setor - tarik;
        
        return saldoAkhir;
    }
}