public class GeneratorPola {

    public String buatPola(int n) {
        String polaHasil = "";

        // 1 Loop utama
        for (int i = 1; i <= n; i++) {
            
            // Branching Tingkat 1
            if (i % 2 == 0) {
                // Nested Branching 1 (Genap)
                if (i > 10) {
                    polaHasil += "X";
                } else {
                    polaHasil += "Y";
                }
            } else {
                // Nested Branching 2 (Ganjil)
                if (i % 3 == 0) {
                    polaHasil += "A";
                } else {
                    polaHasil += "B";
                }
            }
        }
        
        return polaHasil; 
    }
}