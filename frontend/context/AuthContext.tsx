'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import axios from 'axios';

interface AuthContextType {
    token: string | null;
    login: (token: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
    token: null,
    login: () => { },
    logout: () => { },
    isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(null);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // Check local storage on load
        const storedToken = localStorage.getItem('access_token');
        if (storedToken) {
            setToken(storedToken);
            // Configure axios default
            axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        } else {
            // Redirect to login if not already there
            if (pathname !== '/login') {
                router.push('/login');
            }
        }
    }, [pathname, router]);

    const login = (newToken: string) => {
        localStorage.setItem('access_token', newToken);
        setToken(newToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
        router.push('/');
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setToken(null);
        delete axios.defaults.headers.common['Authorization'];
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
};
