import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

const API_BASE = 'http://127.0.0.1:8000/api';

export const AuthProvider = ({ children }) => {
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('access_token'));
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem('refresh_token'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const persistTokens = (access, refresh) => {
    if (access) {
      localStorage.setItem('access_token', access);
      setAccessToken(access);
    }
    if (refresh) {
      localStorage.setItem('refresh_token', refresh);
      setRefreshToken(refresh);
    }
  };

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
  }, []);

  const fetchMe = useCallback(async (token) => {
    try {
      const res = await fetch(`${API_BASE}/auth/me/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
        return data;
      }
    } catch (err) {
      console.error('Error obteniendo el usuario', err);
    }
    return null;
  }, []);

  // Intenta renovar el access token usando el refresh token guardado.
  const tryRefresh = useCallback(async () => {
    const storedRefresh = localStorage.getItem('refresh_token');
    if (!storedRefresh) return null;
    try {
      const res = await fetch(`${API_BASE}/auth/login/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: storedRefresh }),
      });
      if (res.ok) {
        const data = await res.json();
        persistTokens(data.access, data.refresh);
        return data.access;
      }
    } catch (err) {
      console.error('Error renovando el token', err);
    }
    logout();
    return null;
  }, [logout]);

  // Wrapper de fetch que agrega el header Authorization y reintenta una vez si el token expiró.
  const authFetch = useCallback(async (url, options = {}) => {
    let token = localStorage.getItem('access_token');
    const doFetch = (tok) => fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(tok ? { Authorization: `Bearer ${tok}` } : {}),
      },
    });

    let response = await doFetch(token);
    if (response.status === 401 && token) {
      const newToken = await tryRefresh();
      if (newToken) {
        response = await doFetch(newToken);
      }
    }
    return response;
  }, [tryRefresh]);

  const login = async (username, password) => {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Usuario o contraseña incorrectos');
    }
    persistTokens(data.access, data.refresh);
    await fetchMe(data.access);
    return data;
  };

  const register = async (payload) => {
    const res = await fetch(`${API_BASE}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      const firstError = Object.values(data)[0];
      throw new Error(Array.isArray(firstError) ? firstError[0] : (firstError || 'No se pudo registrar el usuario'));
    }
    return data;
  };

  useEffect(() => {
    const init = async () => {
      if (accessToken) {
        const me = await fetchMe(accessToken);
        if (!me) {
          const newToken = await tryRefresh();
          if (newToken) await fetchMe(newToken);
        }
      }
      setLoading(false);
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AuthContext.Provider value={{
      user, accessToken, refreshToken, loading,
      isAuthenticated: !!user,
      isAdmin: !!user?.is_staff,
      login, register, logout, authFetch,
    }}>
      {children}
    </AuthContext.Provider>
  );
};
