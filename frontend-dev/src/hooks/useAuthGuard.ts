import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";

interface UseAuthGuardOptions {
  requiredRole?: "student" | "teacher";
  redirectToLogin?: string;
  redirectToUnauthorized?: string;
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

    if (requiredRole && session.login_type !== requiredRole) {
      navigate(redirectToUnauthorized);
    }
  }, [session, requiredRole, navigate, redirectToLogin, redirectToUnauthorized]);

  return {
    session,
    isAuthenticated: session !== null,
    token: session?.token || "",
    userRole: session?.login_type,
  };
};

export default useAuthGuard;
