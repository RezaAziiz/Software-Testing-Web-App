import org.junit.Assert;
import org.junit.Test;

public class GetSizeKaosTest {
	@Test
	public void Uji_size_M() {
		GetSizeKaos objectTest = new GetSizeKaos();
		char actual = objectTest.getSizeKaos_12(110, 30);
		Assert.assertEquals('M', actual);
	}

	@Test
	public void Uji_size_invalid_dengan_TB_160_dan_BB_lebih_dari_80() {
		GetSizeKaos objectTest = new GetSizeKaos();
		char actual = objectTest.getSizeKaos_12(160, 82);
		Assert.assertEquals(' ', actual);
	}

	@Test
	public void Uji_size_invalid_dengan_TB_173_dan_BB_kurang_dari_60() {
		GetSizeKaos objectTest = new GetSizeKaos();
		char actual = objectTest.getSizeKaos_12(173, 50);
		Assert.assertEquals(' ', actual);
	}

	@Test
	public void Uji_size_X() {
		GetSizeKaos objectTest = new GetSizeKaos();
		char actual = objectTest.getSizeKaos_12(173, 70);
		Assert.assertEquals('X', actual);
	}

	@Test
	public void Uji_size_invalid_dengan_TB_173_dan_BB_lebih_dari_80() {
		GetSizeKaos objectTest = new GetSizeKaos();
		char actual = objectTest.getSizeKaos_12(173, 90);
		Assert.assertEquals(' ', actual);
	}

	@Test
	public void Uji_size_L() {
		GetSizeKaos objectTest = new GetSizeKaos();
		char actual = objectTest.getSizeKaos_12(160, 60);
		Assert.assertEquals('L', actual);
	}

}
