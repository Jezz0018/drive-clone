import { writable } from 'svelte/store';

export const user = writable(null);
export const token = writable(typeof window !== 'undefined' ? localStorage.getItem('token') : null);

export const storageUsage = writable({ used: 0, limit: 10 * 1024 * 1024 * 1024 }); // Default 10GB limit

// UI State for Global Modals
export const ui = writable({
    showUploadModal: false,
    uploadType: 'file' as 'file' | 'folder',
    mimeFilter: undefined as string | undefined
});

token.subscribe((value) => {
    if (typeof window !== 'undefined') {
        if (value) {
            localStorage.setItem('token', value);
        } else {
            localStorage.removeItem('token');
        }
    }
});
