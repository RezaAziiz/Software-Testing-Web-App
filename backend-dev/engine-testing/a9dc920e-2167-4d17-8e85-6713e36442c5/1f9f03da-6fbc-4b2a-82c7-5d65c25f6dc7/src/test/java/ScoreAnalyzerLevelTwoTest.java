import org.junit.Assert;
import org.junit.Test;

public class ScoreAnalyzerLevelTwoTest {
	@Test
	public void TC1() {
		ScoreAnalyzerLevelTwo objectTest = new ScoreAnalyzerLevelTwo();
		String actual = objectTest.analyzeScores(new int[]{80, 90, 100}, 75);
		Assert.assertEquals("Semua Lulus", actual);
	}

	@Test
	public void TC2() {
		ScoreAnalyzerLevelTwo objectTest = new ScoreAnalyzerLevelTwo();
		String actual = objectTest.analyzeScores(new int[]{60, 70, 50}, 75);
		Assert.assertEquals("Tidak Ada yang Lulus", actual);
	}

}
