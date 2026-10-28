
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  getCurrentUser,
  loginUser,
  registerUser,
  type UserProfile,
} from "../lib/api";

interface AuthContextValue {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (
    name: string,
    email: string,
    password: string,
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const TOKEN_KEY = "interviewai_access_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    let active = true;

    async function restoreSession() {
      const savedToken = localStorage.getItem(TOKEN_KEY);

      if (!savedToken) {
        if (active) setLoading(false);
        return;
      }

      try {
        const profile = await getCurrentUser(savedToken);

        if (active) {
          setToken(savedToken);
          setUser(profile);
        }
      } catch {
        localStorage.removeItem(TOKEN_KEY);
      } finally {
        if (active) setLoading(false);
      }
    }

    void restoreSession();

    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const result = await loginUser({ email, password });
      const profile = await getCurrentUser(result.access_token);

      localStorage.setItem(TOKEN_KEY, result.access_token);
      setToken(result.access_token);
      setUser(profile);
    },
    [],
  );

  const signup = useCallback(
    async (name: string, email: string, password: string) => {
      await registerUser({ name, email, password });
      await login(email, password);
    },
    [login],
  );

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, signup, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
