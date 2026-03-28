"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getMe, login as apiLogin, refreshToken, type TokenResponse, type UserResponse } from "./api";

interface AuthState {
  user: UserResponse | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState>({
  user: null,
  token: null,
  loading: true,
  login: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("fiscia_access_token");
    localStorage.removeItem("fiscia_refresh_token");
  }, []);

  // Restore session on mount
  useEffect(() => {
    const stored = localStorage.getItem("fiscia_access_token");
    const storedRefresh = localStorage.getItem("fiscia_refresh_token");

    if (!stored) {
      setLoading(false);
      return;
    }

    getMe(stored)
      .then((u) => {
        setUser(u);
        setToken(stored);
      })
      .catch(async () => {
        // Try refresh
        if (storedRefresh) {
          try {
            const tokens = await refreshToken(storedRefresh);
            localStorage.setItem("fiscia_access_token", tokens.access_token);
            localStorage.setItem("fiscia_refresh_token", tokens.refresh_token);
            const u = await getMe(tokens.access_token);
            setUser(u);
            setToken(tokens.access_token);
          } catch {
            logout();
          }
        } else {
          logout();
        }
      })
      .finally(() => setLoading(false));
  }, [logout]);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await apiLogin(email, password);
    localStorage.setItem("fiscia_access_token", tokens.access_token);
    localStorage.setItem("fiscia_refresh_token", tokens.refresh_token);
    setToken(tokens.access_token);
    const u = await getMe(tokens.access_token);
    setUser(u);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
