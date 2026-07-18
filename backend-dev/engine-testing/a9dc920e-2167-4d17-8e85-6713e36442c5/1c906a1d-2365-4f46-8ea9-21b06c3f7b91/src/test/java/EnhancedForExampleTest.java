import org.junit.Assert;
import org.junit.Test;

public class EnhancedForExampleTest {
	@Test
	public void TC1() {
		EnhancedForExample objectTest = new EnhancedForExample();
		String actual = objectTest.analyzeScores(new int[]{80, 90, 75});
		Assert.assertEquals("Semua Lulus", actual);
	}

}
