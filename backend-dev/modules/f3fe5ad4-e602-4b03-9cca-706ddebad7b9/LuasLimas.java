public class LuasLimas {

	public float luasLimas(float sisiAlas, float tinggiMiring) {
		float luas;
		luas = (sisiAlas * sisiAlas) + (4 * (sisiAlas * tinggiMiring / 2));
		return luas;	
	}
}