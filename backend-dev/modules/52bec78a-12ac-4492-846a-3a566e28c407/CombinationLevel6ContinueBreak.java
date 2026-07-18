/* Deskripsi: 
* Program ini memiliki struktur kombinasi dengan kedalaman 6, 
* dengan statement continue dan break
*/
public class CombinationLevel6ContinueBreak {
    
    public int combinationLevel6ContinueBreak(int batas) {
        int total = 0;

        for (int i = 1; i <= batas; i++) {                  // Level 1
            if (i % 2 == 0) {                               // Level 2
                int j = 1;
                while (j <= 3) {                            // Level 3
                    if ((i + j) % 2 == 0) {                 // Level 4
                        int k = 1;
                        do {                                // Level 5
                            if (k == 2) {                   // Level 6
                                k++;
                                continue;
                            }
                            total += i * j * k;
                            if (total > 100) {
                                break;
                            }
                            k++;
                        } while (k <= 3);
                    }
                    j++;
                }
            }
        }

        return total;
    }
}