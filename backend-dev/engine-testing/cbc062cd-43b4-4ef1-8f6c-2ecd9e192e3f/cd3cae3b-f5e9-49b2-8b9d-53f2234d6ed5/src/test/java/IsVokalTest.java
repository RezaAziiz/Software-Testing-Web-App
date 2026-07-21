import org.junit.Assert;
import org.junit.Test;

public class IsVokalTest {
	@Test
	public void TC_1() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('a');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_2() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('A');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_3() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('i');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_4() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('I');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_5() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('u');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_6() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('U');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_7() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('e');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_8() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('E');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_9() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('o');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_10() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('O');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC_11() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('B');
		Assert.assertEquals(false, actual);
	}

}
