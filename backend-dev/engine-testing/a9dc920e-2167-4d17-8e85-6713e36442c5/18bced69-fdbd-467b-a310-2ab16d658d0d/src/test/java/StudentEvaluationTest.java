import org.junit.Assert;
import org.junit.Test;

public class StudentEvaluationTest {
	@Test
	public void TC1() {
		StudentEvaluation objectTest = new StudentEvaluation();
		String actual = objectTest.evaluateStudents(new String[]{"Andi", "Budi", "Citra"}, new int[]{90, 90, 90});
		Assert.assertEquals("Semua siswa lulus", actual);
	}

}
