/* Program: isVokal
 * Deskripsi: Memeriksa apakah suatu karakter merupakan huruf vokal atau bukan
 * Nama: Muhammad Saiful Islam/141524020
 * Tanggal/versi: 24 Oktober 2014/v.0
 */


public class IsVokal {

    public boolean isVokal(char huruf) {

        boolean vokal = false;
        switch (huruf) {
            case 'a':
                vokal = true;
                break;
            case 'A':
                vokal = true;
                break;
            case 'i':
                vokal = true;
                break;
            case 'I':
                vokal = true;
                break;
            case 'u':
                vokal = true;
                break;
            case 'U':
                vokal = true;
                break;
            case 'e':
                vokal = true;
                break;
            case 'E':
                vokal = true;
                break;
            case 'o':
                vokal = true;
                break;
            case 'O':
                vokal = true;
                break;
            default:
                vokal = false;
        }
        return vokal;
    }
}
