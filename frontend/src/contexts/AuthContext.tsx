import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiService from '@/services/api';

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register?: (data: { username: string; email: string; password: string }) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const me: any = await apiService.getCurrentUser();
          setUser({
            id: String(me?.id ?? ''),
            username: me?.username ?? '',
            email: me?.email ?? '',
            role: me?.role ?? 'user',
          });
        } catch {
          localStorage.removeItem('access_token');
        }
      }
      setIsLoading(false);
    };
    void init();
  }, []);

  const login = async (username: string, password: string) => {
    await apiService.login(username, password);
    const me: any = await apiService.getCurrentUser();
    setUser({
      id: String(me?.id ?? ''),
      username: me?.username ?? '',
      email: me?.email ?? '',
      role: me?.role ?? 'user',
    });
  };

  const register = async (data: { username: string; email: string; password: string }) => {
    // Si el backend no tiene /auth/register, esto fallará y el caller mostrará el error.
    await apiService.register(data as any);
  };

  const logout = () => {
    console.log('AuthContext: Iniciando logout...');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    console.log('AuthContext: Logout completado');
  };

  const value = {
    user,
    login,
    register,
    logout,
    isLoading,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
