import { createContext, useContext, useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { secureStorage } from '@/lib/security';

type User = {
  id: number;
  email: string;
  role: string;
};

type AuthContextType = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User) => void;
  logout: () => void;
  refreshUser: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check if user is logged in on initial load
    const checkAuth = async () => {
      try {
        const storedUser = secureStorage.get<User>('current_user');
        if (storedUser) {
          setUser(storedUser);
        }
      } catch (error) {
        console.error('Failed to check auth status', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = (userData: User) => {
    secureStorage.set('current_user', userData);
    setUser(userData);
    
    // Redirect to the intended page or dashboard
    const from = location.state?.from?.pathname || '/dashboard';
    navigate(from, { replace: true });
  };

  const logout = () => {
    secureStorage.remove('current_user');
    secureStorage.remove('access_token');
    localStorage.removeItem('access_token');
    setUser(null);
    navigate('/');
  };

  const refreshUser = () => {
    const storedUser = secureStorage.get<User>('current_user');
    if (storedUser) {
      setUser(storedUser);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
