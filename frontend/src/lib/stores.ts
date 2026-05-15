import { writable } from 'svelte/store';

export const user = writable(null);
export const token = writable(typeof window !== 'undefined' ? localStorage.getItem('token') : null);

token.subscribe((value) => {
    if (typeof window !== 'undefined') {
        if (value) {
            localStorage.setItem('token', value);
        } else {
            localStorage.removeItem('token');
        }
    }
});
