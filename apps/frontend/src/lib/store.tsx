import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, type UserProfile } from './api';

const ACCESS_KEY = 'myaibuddy.access_token';
const REFRESH_KEY = 'myaibuddy.refresh_token';

interface AuthContextValue {
  user: UserProfile | null;
  loading: boolean;
  token: string | null;
  login: (email: string, password: string) => Promise<UserProfile>;
  register: (email: string, password: string, displayName?: string) => Promise<UserProfile>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function readToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setTokenState] = useState<string | null>(() => readToken());
  const [loading, setLoading] = useState<boolean>(() => Boolean(readToken()));

  const setToken = useCallback((value: string | null) => {
    if (value) localStorage.setItem(ACCESS_KEY, value);
    else localStorage.removeItem(ACCESS_KEY);
    setTokenState(value);
  }, []);

  const loadProfile = useCallback(async (t: string) => {
    const profile = await api.get<UserProfile>('/auth/me', t);
    setUser(profile);
    return profile;
  }, []);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    loadProfile(token)
      .catch(() => {
        localStorage.removeItem(ACCESS_KEY);
        localStorage.removeItem(REFRESH_KEY);
        setTokenState(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, [token, loadProfile]);

  const finishAuth = useCallback(
    async (tokens: { access_token: string; refresh_token: string }) => {
      localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
      setToken(tokens.access_token);
      const profile = await loadProfile(tokens.access_token);
      return profile;
    },
    [loadProfile, setToken],
  );

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await api.post<{ access_token: string; refresh_token: string }>('/auth/login', {
        email,
        password,
      });
      return finishAuth(tokens);
    },
    [finishAuth],
  );

  const register = useCallback(
    async (email: string, password: string, displayName?: string) => {
      await api.post<UserProfile>('/auth/register', {
        email,
        password,
        display_name: displayName || null,
      });
      return login(email, password);
    },
    [login],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setTokenState(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used within AuthProvider');
  return value;
}