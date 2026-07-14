public class LevelSixComplexity {
    public String processExtreme(int dimA, int dimB, int dimC, String keyword) {
        // TINGKAT 1: for
        L1_OUTER: for (int a = 0; a < dimA; a++) {
            int b = 0;
            // TINGKAT 2: while
            L2_WHILE: while (b < dimB) {
                // TINGKAT 3: if
                if (a + b < 500) {
                    // TINGKAT 4: switch
                    switch (b % 2) {
                        case 0:
                            int c = 0;
                            // TINGKAT 5: do-while
                            L5_DEEP_DO: do {
                                // TINGKAT 6: if-else bersarang
                                if (c < keyword.length()) {
                                    char keyChar = keyword.charAt(c);
                                    if (keyChar == 'F') {
                                        // Edge lurus ke akhir fungsi
                                        return "FOUND";
                                    } else if (keyChar == 'C') {
                                        c++;
                                        // Edge memotong ke evaluasi L5
                                        continue L5_DEEP_DO;
                                    } else if (keyChar == 'U') {
                                        // Edge memotong ke evaluasi L2_WHILE
                                        b++;
                                        continue L2_WHILE;
                                    } else if (keyChar == 'B') {
                                        // Edge memecahkan loop terluar L1_OUTER
                                        break L1_OUTER;
                                    }
                                }
                                c++;
                            } while (c < dimC);
                            break;
                        case 1:
                            b++;
                            // Tembus menuju evaluasi L2_WHILE
                            continue L2_WHILE;
                    }
                }
                b++;
            }
        }
        return "NOT_FOUND";
    }
}