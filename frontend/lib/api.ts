import axios from 'axios';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const TOKEN_STORAGE_KEY = 'access_token';

/**
 * Single axios instance for the whole app. The auth token is attached here
 * (via AuthContext's login/logout calls setting the default header) and a
 * 401 response is handled globally by the interceptor AuthContext registers,
 * so no component needs to read localStorage or set headers itself.
 */
export const api = axios.create({
  baseURL: API_BASE_URL,
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}
