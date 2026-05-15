import axios from 'axios';
import { token, user } from './stores';
import { goto } from '$app/navigation';

export const BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: BASE_URL,
});

// Add a request interceptor to attach the JWT token
api.interceptors.request.use(
    (config) => {
        const t = localStorage.getItem('token');
        if (t) {
            config.headers.Authorization = `Bearer ${t}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add a response interceptor to handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            token.set(null);
            user.set(null);
            if (typeof window !== 'undefined') {
                goto('/login');
            }
        }
        return Promise.reject(error);
    }
);

export default api;
