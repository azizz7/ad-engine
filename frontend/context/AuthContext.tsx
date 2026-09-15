'use client';

import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { api, setAuthToken, TOKEN_STORAGE_KEY } from '@/lib/api';

interface AuthContextType {
    token: string | null;
    login: (token: string) => void;
    logout: (reason?: string) => void;
    isAuthenticated: boolean;
    sessionMessage: string | null;
    clearSessionMessage: () => void;
}

const AuthContext = createContext<AuthContextType>({
    token: null,
    login: () => { },
    logout: () => { },
    isAuthenticated: false,
    sessionMessage: null,
    clearSessionMessage: () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(null);
    const [sessionMessage, setSessionMessage] = useState<string | null>(null);
    const router = useRouter();
    const pathname = usePathname();
    // Keep the logout implementation reachable from the axios interceptor,
    // which is registered once and must not close over a stale `pathname`.
    const logoutRef = useRef<(reason?: string) => void>(() => { });

    useEffect(() => {
        const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
        if (storedToken) {
            setToken(storedToken);
            setAuthToken(storedToken);
        } else if (pathname !== '/login') {
            router.push('/login');
        }
        // Only run on mount: this is a one-time "restore session" check, not
        // something that should re-fire on every route change.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const login = (newToken: string) => {
        localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
        setToken(newToken);
        setAuthToken(newToken);
        setSessionMessage(null);
        router.push('/');
    };

    const logout = (reason?: string) => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setToken(null);
        setAuthToken(null);
        if (reason) setSessionMessage(reason);
        router.push('/login');
    };

    useEffect(() => {
        logoutRef.current = logout;
    });

    // Registered once: any 401 from the API (expired/invalid token) forces a
    // clean logout + redirect instead of every caller silently failing.
    useEffect(() => {
        const interceptor = api.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
                    logoutRef.current('Your session has expired. Please sign in again.');
                }
                return Promise.reject(error);
            }
        );
        return () => api.interceptors.response.eject(interceptor);
    }, []);

    return (
        <AuthContext.Provider
            value={{
                token,
                login,
                logout,
                isAuthenticated: !!token,
                sessionMessage,
                clearSessionMessage: () => setSessionMessage(null),
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};
