import { writable } from 'svelte/store';

export interface Toast {
    id: number;
    message: string;
    type: 'success' | 'error' | 'info';
}

function createToastStore() {
    const { subscribe, update } = writable<Toast[]>([]);

    function add(message: string, type: Toast['type'] = 'info') {
        const id = Date.now();
        update(all => [...all, { id, message, type }]);
        setTimeout(() => remove(id), 5000);
    }

    function remove(id: number) {
        update(all => all.filter(t => t.id !== id));
    }

    return {
        subscribe,
        success: (m: string) => add(m, 'success'),
        error: (m: string) => add(m, 'error'),
        info: (m: string) => add(m, 'info'),
        remove
    };
}

export const toasts = createToastStore();
