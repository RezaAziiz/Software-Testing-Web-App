import org.junit.Assert;
import org.junit.Test;


public class CekKelulusanTest {
 	@Test 
 	public void Nilai_lebih_dari_75() { 
 		CekKelulusan objectTest = new CekKelulusan(); 
		int actual = objectTest.cekKelulusan(90); 
		Assert.assertEquals(1, actual);
 	}

	@Test 
 	public void Nilai_kurang_dari_75() { 
 		CekKelulusan objectTest = new CekKelulusan(); 
		int actual = objectTest.cekKelulusan(60); 
		Assert.assertEquals(0, actual);
 	}

}