import { AuthContext } from "@/hooks/use-auth";
import { User } from "@/lib/types";
import {
  FC,
  ReactNode,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [tokenExpiry, setTokenExpiry] = useState<number | null>(null);

  // Use a ref to track an in-flight refresh token call
  const refreshPromiseRef = useRef<Promise<string | null> | null>(null);

  const refreshAccessToken = useCallback(async (): Promise<string | null> => {
    // If token exists and is not expired, return it
    if (accessToken && tokenExpiry && Date.now() < tokenExpiry) {
      return accessToken;
    }

    // If a refresh is already in progress, return that promise
    if (refreshPromiseRef.current) {
      return refreshPromiseRef.current;
    }

    // Otherwise, start a new refresh request
    refreshPromiseRef.current = (async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/login/refresh-token', {
          method: 'POST',
          credentials: 'include',
        });
        if (response.ok) {
          const data = await response.json();
          // Assume the token expires in 15 minutes; refresh 1 minute early
          setAccessToken(data.access_token);
          setTokenExpiry(Date.now() + 14 * 60 * 1000);
          return data.access_token;
        } else {
          // If refresh fails, clear token info
          setAccessToken(null);
          setTokenExpiry(null);
          return null;
        }
      } catch (error) {
        console.error('Token refresh failed:', error);
        setAccessToken(null);
        setTokenExpiry(null);
        return null;
      }
    })();

    const token = await refreshPromiseRef.current;
    // Clear the in-flight promise once done
    refreshPromiseRef.current = null;
    return token;
  }, [accessToken, tokenExpiry]);

  const login = async (username: string, password: string): Promise<void> => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/login/access-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
        }),
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access_token);
        setTokenExpiry(Date.now() + 14 * 60 * 1000);
        setIsAuthenticated(true);
        setUser({ id: '', name: 'Dummy' });
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await fetch('http://127.0.0.1:8000/api/v1/login/logout', {
        method: 'POST',
        credentials: 'include',
      });
      setIsAuthenticated(false);
      setUser(null);
      setAccessToken(null);
      setTokenExpiry(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const fetchWithAuthOriginal = async (url: string, options: RequestInit = {}): Promise<Response> => {
    let token = await refreshAccessToken();
    const fetchOptions: RequestInit = {
      ...options,
      headers: {
        ...options.headers,
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      credentials: 'include',
    };

    try {
      let response = await fetch(url, fetchOptions);

      if (response.status === 401) {
        // If the token was rejected, try refreshing it once more.
        token = await refreshAccessToken();
        if (token) {
          fetchOptions.headers = {
            ...fetchOptions.headers,
            'Authorization': `Bearer ${token}`,
          };
          response = await fetch(url, fetchOptions);
        } else {
          // If refresh fails, user needs to log in again.
          setIsAuthenticated(false);
          setUser(null);
          throw new Error('Session expired');
        }
      }
      if (!response.ok) {
        throw new Error('Request failed');
      }
      return response;
    } catch (error) {
      console.error('Fetch error:', error);
      throw error;
    }
  };

  const fetchWithAuth = (input: RequestInfo, init?: RequestInit) => {
    if (typeof input === 'string') {
      return fetchWithAuthOriginal(input, init);
    } else {
      return fetchWithAuthOriginal(input.url, { ...init, ...input });
    }
  };

  useEffect(() => {
    // This effect checks auth status on mount.
    refreshAccessToken().then(token => {
      setIsAuthenticated(!!token);
    });
    // NOTE: In development with React StrictMode, this effect may run twice.
  }, [refreshAccessToken]);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout, fetchWithAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;