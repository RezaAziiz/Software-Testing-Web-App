public class ComplexNestedLoop {

    public String complexNestedLoop(int limit) {

        int score = 0;

        for (int a = 0; a < limit; a++) {

            for (int b = 0; b < limit; b++) {

                for (int c = 0; c < limit; c++) {

                    for (int d = 0; d < limit; d++) {

                        for (int e = 0; e < limit; e++) {

                            if (a == b) {

                                if (c == d) {

                                    score++;

                                    if (score > 5) {
                                        return "MATCH";
                                    }

                                } else {

                                    if (e % 2 == 0) {
                                        continue;
                                    }

                                }

                            } else {

                                if (a + b > c + d) {

                                    score += 2;

                                    if (score > 10) {
                                        break;
                                    }

                                } else if (e > 2) {

                                    score--;

                                } else {

                                    score += 3;

                                }
                            }

                        }
                    }
                }
            }
        }

        if (score > 0) {
            return "POSITIVE";
        }

        return "NEGATIVE";
    }
}