import { AuthContext } from "@/hooks/use-auth";
import { User } from "@/lib/types";
import {
  FC,
  ReactNode,
  useCallback,
  useEffect,
  useState
} from "react";

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  const refreshAccessToken = useCallback(async (): Promise<string | null> => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/login/refresh-token', {
        method: 'POST',
        credentials: 'include', // This is crucial for sending the HttpOnly cookie
      });
      if (response.ok) {
        const data = await response.json();
        return data.access_token;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
    return null;
  }, []);

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
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
    let accessToken = await refreshAccessToken();
    
    const fetchOptions: RequestInit = {
      ...options,
      headers: {
        ...options.headers,
        ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
      },
      credentials: 'include',
    };

    try {
      let response = await fetch(url, fetchOptions);

      if (response.status === 401) {
        // Token might be expired, try to refresh again
        accessToken = await refreshAccessToken();
        if (accessToken) {
          fetchOptions.headers = {
            ...fetchOptions.headers,
            'Authorization': `Bearer ${accessToken}`,
          };
          response = await fetch(url, fetchOptions);
        } else {
          // Refresh failed, user needs to login again
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

  useEffect(() => {
    // Check authentication status on mount
    refreshAccessToken().then(token => setIsAuthenticated(!!token));
  }, [refreshAccessToken]);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout, fetchWithAuth }}>
      {children}
    </AuthContext.Provider>
  );
};



export default AuthProvider;
