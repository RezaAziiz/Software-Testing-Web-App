import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { decodeJwtPayload } from "@/lib/apiClient";

interface UseAuthGuardOptions {
  requiredRole?: "student" | "teacher";
  redirectToLogin?: string;
  redirectToUnauthorized?: string;
  redirectToError?: string;
}

export interface UserSession {
  login_type?: string;
  token?: string;
  [key: string]: any;
}

export const useAuthGuard = (options: UseAuthGuardOptions = {}) => {
  const {
    requiredRole,
    redirectToLogin = "/login",
    redirectToUnauthorized = "/dashboard-teacher",
    redirectToError = "/error",
  } = options;

  const navigate = useNavigate();

  // Safely parse session data from localStorage
  const session: UserSession | null = useMemo(() => {
    try {
      const sessionData = localStorage.getItem("session");
      if (!sessionData) return null;
      return JSON.parse(sessionData);
    } catch (error) {
      console.error("Failed to parse user session JSON from localStorage:", error);
      return null;
    }
  }, []);

  useEffect(() => {
    if (!session) {
      navigate(redirectToLogin);
      return;
    }

    // 1. Validasi proaktif kedaluwarsa token JWT
    if (session.token) {
      const payload = decodeJwtPayload(session.token);
      if (payload && typeof payload.exp === "number") {
        const nowInMs = Date.now();
        const expInMs = payload.exp * 1000;

        if (expInMs <= nowInMs) {
          // Token sudah expired
          localStorage.removeItem("session");
          navigate(redirectToError);
          return;
        }

        // Pasang timer aktif untuk redirect tepat saat token habis di latar belakang
        const timeRemaining = expInMs - nowInMs;
        const timer = setTimeout(() => {
          localStorage.removeItem("session");
          navigate(redirectToError);
        }, timeRemaining);

        return () => clearTimeout(timer);
      }
    }

    if (requiredRole && session.login_type !== requiredRole) {
      navigate(redirectToUnauthorized);
    }
  }, [
    session,
    requiredRole,
    navigate,
    redirectToLogin,
    redirectToUnauthorized,
    redirectToError,
  ]);

  return {
    session,
    isAuthenticated: session !== null,
    token: session?.token || "",
    userRole: session?.login_type,
  };
};

export default useAuthGuard;

