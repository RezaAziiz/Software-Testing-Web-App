import org.junit.Assert;
import org.junit.Test;

public class IsVokalTest {
	@Test
	public void TC1() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('a');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC2() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('A');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC3() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('I');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC4() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('i');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC5() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('u');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC6() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('U');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC7() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('E');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC8() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('e');
		Assert.assertEquals(true, actual);
	}

	@Test
	public void TC9() {
		IsVokal objectTest = new IsVokal();
		boolean actual = objectTest.isVokal('O');
		Assert.assertEquals(true, actual);
	}

}
