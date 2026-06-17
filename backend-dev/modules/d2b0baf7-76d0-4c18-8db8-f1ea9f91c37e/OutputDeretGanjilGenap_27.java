public class OutputDeretGanjilGenap_27 {
    
    public String jalankanDeret(int batasAkhir) {
        //Body atau isi dri method jalankanDeret()
        String hasil = ""; 

        for (int i = 1; i <= batasAkhir; i++) {
            if (i % 2 == 0) {
                hasil += "Angka " + i + " adalah Genap\n";
            } 
            else {
                hasil += "Angka " + i + " adalah Ganjil\n";
            } 
        } 
        return hasil; 
    }
}