"use client";

import * as React from "react";
import { usePathname, useRouter } from "next/navigation";

import { api } from "@/lib/api";
import type { UserProfile } from "@/lib/types";

type AuthContextValue = {
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: (refreshToken?: string) => Promise<void>;
};

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

type AuthProviderProps = {
  children: React.ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = React.useState<UserProfile | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  const refresh = React.useCallback(async () => {
    try {
      setError(null);
      const current = await api.me();
      setUser(current);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = React.useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.login(email, password);
        if (data.user) {
          setUser(data.user);
        } else {
          await refresh();
        }
        router.push("/tableau-de-bord");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Connexion impossible.");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [refresh, router]
  );

  const logout = React.useCallback(
    async (refreshToken?: string) => {
      setLoading(true);
      try {
        await api.logout(refreshToken ?? "");
      } catch {
        // ignore remote logout failure
      } finally {
        setUser(null);
        setLoading(false);
        if ((pathname ?? "").startsWith("/tableau-de-bord") || (pathname ?? "").startsWith("/dashboard")) {
          router.push("/auth/connexion");
        }
      }
    },
    [pathname, router]
  );

  const value = React.useMemo(
    () => ({ user, loading, error, refresh, login, logout }),
    [user, loading, error, refresh, login, logout]
  );

  return React.createElement(AuthContext.Provider, { value }, children);
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth doit etre utilise dans AuthProvider.");
  }
  return context;
}

