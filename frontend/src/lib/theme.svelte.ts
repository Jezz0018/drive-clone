import { browser } from '$app/environment';

class ThemeManager {
    current = $state(
        browser ? (localStorage.getItem('theme') || 'light') : 'light'
    );

    constructor() {
        if (browser) {
            this.updateDocument();
        }
    }

    toggle() {
        this.current = this.current === 'light' ? 'dark' : 'light';
        if (browser) {
            localStorage.setItem('theme', this.current);
            this.updateDocument();
        }
    }

    init() {
        if (browser) {
            this.updateDocument();
        }
    }

    updateDocument() {
        if (!browser) return;
        if (this.current === 'dark') {
            document.documentElement.classList.add('dark');
            document.documentElement.style.colorScheme = 'dark';
        } else {
            document.documentElement.classList.remove('dark');
            document.documentElement.style.colorScheme = 'light';
        }
    }
}

export const theme = new ThemeManager();
