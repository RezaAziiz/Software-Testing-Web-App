public class DroneSearchMission {
    public String searchTarget(int totalLayers,
            int totalRows,
            int totalPoints,
            String instructionSequence) {
        L1_OUTER: for (int layer = 0; layer < totalLayers; layer++) {
            int row = 0;
            L2_WHILE: while (row < totalRows) {
                if (layer + row < 500) {
                    switch (row % 2) {
                        case 0:
                            int point = 0;
                            L5_DEEP_DO: do {
                                if (point < instructionSequence.length()) {
                                    char instruction = instructionSequence.charAt(point);
                                    if (instruction == 'F') {
                                        return "FOUND";
                                    } else if (instruction == 'C') {
                                        point++;
                                        continue L5_DEEP_DO;
                                    } else if (instruction == 'U') {
                                        row++;
                                        continue L2_WHILE;
                                    } else if (instruction == 'B') {
                                        break L1_OUTER;
                                    }
                                }
                                point++;
                            } while (point < totalPoints);
                            break;
                        case 1:
                            row++;
                            continue L2_WHILE;
                    }
                }
                row++;
            }
        }
        return "NOT_FOUND";
    }
}