import { renderHook } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useAuthGuard } from '@/hooks/useAuthGuard';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('useAuthGuard - Unit Test', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  // TC-FE-AUTH-01: Validasi Sesi Kosong
  it('TC-FE-AUTH-01: returns isAuthenticated: false and redirects to /login when localStorage has no session', () => {
    localStorage.removeItem('session');

    const { result } = renderHook(() => useAuthGuard());

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.session).toBeNull();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  // TC-FE-AUTH-02: Pembacaan Sesi Valid
  it('TC-FE-AUTH-02: parses valid student session and returns isAuthenticated: true with role and token', () => {
    const validSession = {
      login_type: 'student',
      token: 'jwt-student-token-123',
      name: 'Reza',
    };
    localStorage.setItem('session', JSON.stringify(validSession));

    const { result } = renderHook(() => useAuthGuard());

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.userRole).toBe('student');
    expect(result.current.token).toBe('jwt-student-token-123');
    expect(result.current.session).toEqual(validSession);
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  // TC-FE-AUTH-03: Penanganan Format JSON Rusak
  it('TC-FE-AUTH-03: catches malformed JSON safely via try-catch without crash and redirects to /login', () => {
    localStorage.setItem('session', '{ CORRUPTED_NON_JSON_DATA %%%');
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const { result } = renderHook(() => useAuthGuard());

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.session).toBeNull();
    expect(consoleErrorSpy).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');

    consoleErrorSpy.mockRestore();
  });

  // TC-FE-AUTH-04: Proteksi Hak Akses Peran Akun
  it('TC-FE-AUTH-04: redirects to /dashboard-teacher when requiredRole is student but user is a teacher', () => {
    const teacherSession = {
      login_type: 'teacher',
      token: 'teacher-token-456',
    };
    localStorage.setItem('session', JSON.stringify(teacherSession));

    const { result } = renderHook(() => useAuthGuard({ requiredRole: 'student' }));

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.userRole).toBe('teacher');
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard-teacher');
  });

  // TC-FE-AUTH-05: Kustomisasi Rute Pengalihan
  it('TC-FE-AUTH-05: executes redirect to custom configured URL paths', () => {
    // Test custom login redirect
    localStorage.removeItem('session');
    renderHook(() =>
      useAuthGuard({
        redirectToLogin: '/custom-login-page',
      })
    );
    expect(mockNavigate).toHaveBeenCalledWith('/custom-login-page');

    mockNavigate.mockClear();

    // Test custom unauthorized redirect
    localStorage.setItem('session', JSON.stringify({ login_type: 'teacher' }));
    renderHook(() =>
      useAuthGuard({
        requiredRole: 'student',
        redirectToUnauthorized: '/custom-unauthorized-page',
      })
    );
    expect(mockNavigate).toHaveBeenCalledWith('/custom-unauthorized-page');
  });
});
