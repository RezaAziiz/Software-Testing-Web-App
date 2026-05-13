public class TampilSuhu_10 {

    public String tampilSuhu(int suhu) {
        if (suhu < 0) {
            return "Cair";
        } else {
            if (suhu <= 100) {
                return "Padat";
            } else {
                return "Gas";
            }
        }
    }
}