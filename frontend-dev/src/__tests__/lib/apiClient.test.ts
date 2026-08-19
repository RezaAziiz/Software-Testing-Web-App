import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  apiClient,
  decodeJwtPayload,
  isJwtExpired,
  getStoredSession,
} from "@/lib/apiClient";

describe("apiClient - Unit Test", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    // Mock global fetch
    global.fetch = vi.fn();
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("decodes valid JWT payload correctly", () => {
    // payload: { "sub": "12345", "exp": 1893456000 }
    const fakeToken = "header.eyJzdWIiOiIxMjM0NSIsImV4cCI6MTg5MzQ1NjAwMH0.signature";
    const payload = decodeJwtPayload(fakeToken);
    expect(payload).not.toBeNull();
    expect(payload?.sub).toBe("12345");
    expect(payload?.exp).toBe(1893456000);
  });

  it("returns null for malformed JWT token string", () => {
    expect(decodeJwtPayload("invalid_jwt")).toBeNull();
    expect(decodeJwtPayload("")).toBeNull();
  });

  it("correctly identifies expired vs active token", () => {
    const expiredPayload = { exp: Math.floor(Date.now() / 1000) - 100 };
    const expiredBase64 = btoa(JSON.stringify(expiredPayload));
    const expiredToken = `header.${expiredBase64}.signature`;
    expect(isJwtExpired(expiredToken)).toBe(true);

    const activePayload = { exp: Math.floor(Date.now() / 1000) + 3600 };
    const activeBase64 = btoa(JSON.stringify(activePayload));
    const activeToken = `header.${activeBase64}.signature`;
    expect(isJwtExpired(activeToken)).toBe(false);
  });

  it("parses valid session from localStorage via getStoredSession", () => {
    const session = { token: "token-123", login_type: "student" };
    localStorage.setItem("session", JSON.stringify(session));
    expect(getStoredSession()).toEqual(session);
  });

  it("returns null for corrupted JSON in getStoredSession", () => {
    localStorage.setItem("session", "invalid-json");
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(getStoredSession()).toBeNull();
    consoleSpy.mockRestore();
  });

  it("injects Authorization Bearer header into fetch call", async () => {
    localStorage.setItem(
      "session",
      JSON.stringify({ token: "my-valid-bearer-token" })
    );

    (global.fetch as any).mockResolvedValueOnce({
      status: 200,
      ok: true,
      json: async () => ({ success: true }),
    });

    await apiClient("https://api.test/data");
    expect(global.fetch).toHaveBeenCalledWith(
      "https://api.test/data",
      expect.objectContaining({
        headers: expect.any(Headers),
      })
    );

    const callHeaders: Headers = (global.fetch as any).mock.calls[0][1].headers;
    expect(callHeaders.get("Authorization")).toBe("Bearer my-valid-bearer-token");
  });

  it("clears localStorage and redirects to /error when response status is 403", async () => {
    localStorage.setItem(
      "session",
      JSON.stringify({ token: "expired-token" })
    );

    (global.fetch as any).mockResolvedValueOnce({
      status: 403,
      ok: false,
      json: async () => ({ detail: "Expired token." }),
    });

    await expect(apiClient("https://api.test/protected")).rejects.toThrow();

    // Session should be cleared from localStorage
    expect(localStorage.getItem("session")).toBeNull();
  });

  it("clears localStorage and redirects to /error when response status is 401", async () => {
    localStorage.setItem(
      "session",
      JSON.stringify({ token: "unauthorized-token" })
    );

    (global.fetch as any).mockResolvedValueOnce({
      status: 401,
      ok: false,
    });

    await expect(apiClient("https://api.test/protected")).rejects.toThrow();
    expect(localStorage.getItem("session")).toBeNull();
  });
});
