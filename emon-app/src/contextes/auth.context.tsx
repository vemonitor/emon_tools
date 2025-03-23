import { AuthContext } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import { User } from "@/lib/types";
import { getApiUrl } from "@/lib/utils";
import {
  FC,
  ReactNode,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | undefined>(undefined);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [tokenExpiry, setTokenExpiry] = useState<number | null>(null);
  const { toast } = useToast()
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
        const response = await fetch(
          getApiUrl(`/api/v1/login/refresh-token/`),
          {
            method: 'POST',
            credentials: 'include',
          }
        );
        if (response.ok) {
          const data = await response.json();
          // Assume the token expires in 15 minutes; refresh 1 minute early
          setAccessToken(data.access_token);
          setTokenExpiry(Date.now() + 14 * 60 * 1000);
          return data.access_token;
        } else {
          // If refresh fails, clear token info
          reset();
          return null;
        }
      } catch (error) {
        console.error('Token refresh failed:', error);
        reset();
        return null;
      }
    })();

    const token = await refreshPromiseRef.current;
    // Clear the in-flight promise once done
    refreshPromiseRef.current = null;
    return token;
  }, [accessToken, tokenExpiry]);

  const reset = () => {
    setIsAuthenticated(false);
    setUser(undefined);
    setAccessToken(null);
    setTokenExpiry(null);
  }

  const login = async (username: string, password: string): Promise<void> => {
    try {
      const response = await fetch(
        getApiUrl(`/api/v1/login/access-token/`),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username,
            password,
          }),
          credentials: 'include',
        }
      );
      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access_token);
        setTokenExpiry(Date.now() + 14 * 60 * 1000);
        setIsAuthenticated(true);
        await getCurrentUser();
      } else {
        reset();
        toast({
            title: "Login failed",
            description: 'Please verify your credentials and try again.',
        })
        throw new Error('Login failed');
      }
    } catch (error) {
      reset();
      console.error('Login error:', error);
      throw new Error('Login error');
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await fetch(
        getApiUrl(`/api/v1/login/logout/`),
        {
          method: 'POST',
          credentials: 'include',
        }
      );
      reset();
    } catch (error) {
      reset();
      console.error('Logout failed:', error);
    }
  };

  const getCurrentUser = async (): Promise<void> => {
    try {
      //if(isAuthenticated === true){
        const response = await fetchWithAuth(
          '/api/v1/users/me/',
          {
            method: 'GET',
          }
        )
        if (response.ok){
          const user = await response.json();
          setUser(user);
        }else{
          reset();
          throw new Error('Current User');
        }
    } catch (error) {
      reset();
      console.error('Unable to get current user: ', error);
      toast({
          title: "Error",
          description: 'Unable to get current user.',
      })
    }
  }

  const fetchWithAuthOriginal = async (
    url: string,
    options: RequestInit = {}
  ): Promise<Response> => {
    let token = null;
    try{
      token = await refreshAccessToken();
    } catch (error) {
      console.error('Refresh token error:', error);
      toast({
          title: "Error",
          description: 'Session expired.',
      })
    }
    
    
    const fetchOptions: RequestInit = {
      ...options,
      headers: {
        ...options.headers,
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      credentials: 'include',
    };

    try {
      let response = await fetch(
        getApiUrl(url),
        fetchOptions
      );

      if (response.status === 401) {
        // If the token was rejected, try refreshing it once more.
        token = await refreshAccessToken();
        if (token) {
          fetchOptions.headers = {
            ...fetchOptions.headers,
            'Authorization': `Bearer ${token}`,
          };
          response = await fetch(
            getApiUrl(url),
            fetchOptions
          );
        } else {
          // If refresh fails, user needs to log in again.
          reset();
          toast({
              title: "Error",
              description: 'Session expired.',
          })
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

  const refreshUser = async (): Promise<void> => {
    await getCurrentUser();
  };

  useEffect(() => {
    // This effect checks auth status on mount.
    refreshAccessToken().then(async (token) => {
      setIsAuthenticated(!!token);
      if(!user && isAuthenticated){
        await getCurrentUser();
      }
    });
    // NOTE: In development with React StrictMode, this effect may run twice.
  }, [refreshAccessToken]);

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      login,
      logout,
      fetchWithAuth,
      refreshUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;