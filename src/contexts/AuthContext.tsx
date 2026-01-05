import React, { createContext, useContext, useEffect, useState } from 'react';
import { authApi, type User, type Organization, type AuthData } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  organization: Organization | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
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
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const authData = await authApi.getCurrentUser();
        setUser(authData.user);
        setOrganization(authData.organization);
      } catch (error) {
        // User is not authenticated
        console.log('User not authenticated');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const authData = await authApi.login({ email, password });
      setUser(authData.user);
      setOrganization(authData.organization);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: any) => {
    setIsLoading(true);
    try {
      const authData = await authApi.register(data);
      setUser(authData.user);
      setOrganization(authData.organization);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authApi.logout();
      setUser(null);
      setOrganization(null);
    } catch (error) {
      console.error('Logout error:', error);
      // Clear state anyway
      setUser(null);
      setOrganization(null);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      const authData = await authApi.getCurrentUser();
      setUser(authData.user);
      setOrganization(authData.organization);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // If refresh fails, user might be logged out
      setUser(null);
      setOrganization(null);
    }
  };

  const value: AuthContextType = {
    user,
    organization,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};