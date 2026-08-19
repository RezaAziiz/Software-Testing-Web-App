/**
 * Centralized API Client with Automatic Session Expiration Handling
 * Mengelola request HTTP, injeksi token autentikasi, serta mendeteksi
 * respons 401 / 403 (Sesi Habis) untuk langsung mengalihkan ke /error.
 */

export interface UserSession {
  login_type?: string;
  token?: string;
  [key: string]: any;
}

/**
 * Membaca dan mem-parsing data sesi dari localStorage secara aman.
 */
export const getStoredSession = (): UserSession | null => {
  try {
    const sessionData = localStorage.getItem("session");
    if (!sessionData) return null;
    return JSON.parse(sessionData);
  } catch (error) {
    console.error("Failed to parse user session JSON from localStorage:", error);
    return null;
  }
};

/**
 * Decode JWT token payload secara aman tanpa library eksternal.
 */
export const decodeJwtPayload = (token: string): { exp?: number; [key: string]: any } | null => {
  try {
    if (!token || typeof token !== "string") return null;
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    
    // Handle base64url to base64
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Failed to decode JWT token payload:", error);
    return null;
  }
};

/**
 * Memeriksa apakah token JWT sudah kedaluwarsa berdasarkan klaim 'exp'.
 */
export const isJwtExpired = (token: string): boolean => {
  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload.exp !== "number") return false;
  // exp dalam detik, Date.now() dalam milidetik
  return payload.exp * 1000 <= Date.now();
};

/**
 * Membersihkan sesi dari storage dan mengarahkan pengguna langsung ke /error.
 */
export const handleSessionExpiredRedirect = () => {
  try {
    localStorage.removeItem("session");
  } catch (e) {
    console.error("Failed to clear session from localStorage:", e);
  }

  // Pure background redirect ke /error
  if (typeof window !== "undefined" && window.location) {
    if (window.location.pathname !== "/error") {
      window.location.href = "/error";
    }
  }
};

/**
 * Pembungkus fetch terpusat yang otomatis menyisipkan token dan menangani error 401/403.
 */
export async function apiClient(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const session = getStoredSession();
  const token = session?.token || import.meta.env.VITE_API_KEY || "";

  // 1. Pengecekan proaktif: Jika token JWT sudah expired sebelum request dikirim
  if (token && isJwtExpired(token)) {
    handleSessionExpiredRedirect();
    throw new Error("Forbidden: Session has expired");
  }

  // 2. Siapkan headers dengan Authorization Bearer
  const headers = new Headers(options.headers || {});
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // 3. Pengecekan reaktif: Jika backend mengembalikan 401 Unauthorized atau 403 Forbidden
  if (response.status === 401 || response.status === 403) {
    handleSessionExpiredRedirect();
    throw new Error("Forbidden: Access is denied / Session expired");
  }

  return response;
}

export default apiClient;
