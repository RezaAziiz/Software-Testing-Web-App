public class NestedLoopExample3 {

    public String nestedLoopExample3(int limit) {

        for (int i = 0; i < limit; i++) {

            for (int j = 0; j < limit; j++) {

                for (int k = 0; k < limit; k++) {

                    if (i == j) {

                        if (j == k) {
                            return "Equal";
                        }

                    }

                }
            }
        }

        return "Different";
    }
}