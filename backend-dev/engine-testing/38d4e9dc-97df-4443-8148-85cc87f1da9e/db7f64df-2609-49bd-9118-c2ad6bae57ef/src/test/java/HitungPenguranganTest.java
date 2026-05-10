import org.junit.Assert;
import org.junit.Test;


public class HitungPenguranganTest {
 	@Test 
 	public void Ingin_memverifikasi_proses_pengurangan() { 
 		HitungPengurangan objectTest = new HitungPengurangan(); 
		int actual = objectTest.hitungPengurangan(4,2); 
		Assert.assertEquals(2, actual);
 	}

}