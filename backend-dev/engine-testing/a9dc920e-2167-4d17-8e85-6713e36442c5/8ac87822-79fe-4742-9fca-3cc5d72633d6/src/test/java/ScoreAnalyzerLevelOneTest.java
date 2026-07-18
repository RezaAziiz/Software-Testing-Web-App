import org.junit.Assert;
import org.junit.Test;

public class ScoreAnalyzerLevelOneTest {
	@Test
	public void TC1() {
		ScoreAnalyzerLevelOne objectTest = new ScoreAnalyzerLevelOne();
		String actual = objectTest.analyzeScores(new int[]{80, 90, 85}, 75);
		Assert.assertEquals("Ada Siswa yang Lulus", actual);
	}

	@Test
	public void TC2() {
		ScoreAnalyzerLevelOne objectTest = new ScoreAnalyzerLevelOne();
		String actual = objectTest.analyzeScores(new int[]{60, 70, 50}, 75);
		Assert.assertEquals("Tidak Ada yang Lulus", actual);
	}

}
