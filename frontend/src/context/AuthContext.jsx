import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import api, { fetchData } from '../services/api';

const AuthContext = createContext(null);

function clearAuthTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

function isAuthError(error) {
  const status = error?.response?.status;
  return status === 401 || status === 403;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const data = await fetchData(api.get('/auth/me'));
      setUser(data);
    } catch (error) {
      if (isAuthError(error)) {
        clearAuthTokens();
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email, password) => {
    const tokens = await fetchData(api.post('/auth/login', { email, password }));
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    await loadUser();
  };

  const register = async (payload) => {
    await fetchData(api.post('/auth/register', payload));
    await login(payload.email, payload.password);
  };

  const logout = () => {
    clearAuthTokens();
    setUser(null);
  };

  const refreshUser = loadUser;

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshUser, isAuthenticated: !!user }),
    [user, loading, login, register, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
