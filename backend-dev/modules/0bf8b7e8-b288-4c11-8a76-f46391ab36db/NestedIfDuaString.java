public class NestedIfDuaString {
    public String nestedIfDuaString(int nilai, int kehadiran) {
        String result = "Tidak Lulus";
        if (nilai >= 75) { // level 1
            if (kehadiran >= 80) { // level 2
                result = "Lulus";
            }
        }
        return result;
    }
}