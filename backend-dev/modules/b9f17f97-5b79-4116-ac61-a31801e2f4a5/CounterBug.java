public class CounterBug {

    public String checkCounter(int limit) {
        int counter = 0;

        while (counter < limit) {

            counter++;

            if (counter > 2) {
                return "Error";
            }
        }

        return "OK";
    }
}