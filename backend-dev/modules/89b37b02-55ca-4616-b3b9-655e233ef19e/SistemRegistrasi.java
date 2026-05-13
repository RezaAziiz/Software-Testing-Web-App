public class SistemRegistrasi {

    public String validasiAkun(int umur, String role, String password) {
        String status = "DITOLAK";

        // KASUS 1: Tidak ada spasi antara if dan kondisinya
        if(umur<18){
            return "UMUR_TIDAK_CUKUP";
        }

        // KASUS 2: Blok 'else' dipisah dengan banyak enter
        if (role.equals("ADMIN")) {
            status = "AKSES_ADMIN_DIBERIKAN";
        } 
        
        
        else 
        
        
        {
            status = "AKSES_USER_DIBERIKAN";
        }

        // KASUS 3: Penulisan IF-ELSE berantai tanpa kurung kurawal { } 
        if (password.length() < 8)
            status = status + "_TAPI_PASSWORD_LEMAH";
        else
            status = status + "_DAN_PASSWORD_KUAT";

        // KASUS 4: Jebakan komentar yang akan menipu String Matching
        for(int i = 0; i < 2; i++) {
            status = status + ""; // proses if pengecekan keamanan tambahan
        }

        return status;
    }
}