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
        if (this.current === 'light') {
            this.current = 'dark';
        } else if (this.current === 'dark') {
            this.current = 'monochrome';
        } else {
            this.current = 'light';
        }

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
        document.documentElement.classList.remove('dark', 'monochrome');
        
        if (this.current === 'dark') {
            document.documentElement.classList.add('dark');
            document.documentElement.style.colorScheme = 'dark';
        } else if (this.current === 'monochrome') {
            document.documentElement.classList.add('monochrome');
            document.documentElement.style.colorScheme = 'light';
        } else {
            document.documentElement.style.colorScheme = 'light';
        }
    }
}

export const theme = new ThemeManager();
