import org.junit.Assert;
import org.junit.Test;

public class RemedialEvaluationTest {
	@Test
	public void TC1() {
		RemedialEvaluation objectTest = new RemedialEvaluation();
		String actual = objectTest.evaluateClass(new int[]{80, 95, 90}, 75);
		Assert.assertEquals("Tidak Perlu Remedial", actual);
	}

	@Test
	public void TC2() {
		RemedialEvaluation objectTest = new RemedialEvaluation();
		String actual = objectTest.evaluateClass(new int[]{50, 50, 50}, 75);
		Assert.assertEquals("Seluruh Siswa Remedial", actual);
	}

	@Test
	public void TC3() {
		RemedialEvaluation objectTest = new RemedialEvaluation();
		String actual = objectTest.evaluateClass(new int[]{-1, 70}, 75);
		Assert.assertEquals("Seluruh Siswa Remedial", actual);
	}

	@Test
	public void TC4() {
		RemedialEvaluation objectTest = new RemedialEvaluation();
		String actual = objectTest.evaluateClass(new int[]{60, 60, 90}, 75);
		Assert.assertEquals("Sebagian Siswa Remedial", actual);
	}

}
