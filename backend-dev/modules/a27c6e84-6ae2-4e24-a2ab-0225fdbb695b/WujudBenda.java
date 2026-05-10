public class WujudBenda {
    public String wujudBenda(float suhu) {
        if (suhu >= 0 && suhu <= 100) {
            return "Cair";
        } else if (suhu > 100) {
            return "Uap";
        } else {
            return "Padat";
        }
    }
}
