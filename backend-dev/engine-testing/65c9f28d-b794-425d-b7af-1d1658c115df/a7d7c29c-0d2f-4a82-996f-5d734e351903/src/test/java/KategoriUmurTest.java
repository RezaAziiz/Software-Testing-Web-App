import org.junit.Assert;
import org.junit.Test;


public class KategoriUmurTest {
 	@Test 
 	public void Umur_di_bawah_12() { 
 		KategoriUmur objectTest = new KategoriUmur(); 
		String actual = objectTest.kategoriUmur(10); 
		Assert.assertEquals("Anak-anak", actual);
 	}

}