import { browser } from '$app/environment';

function createTheme() {
    let current = $state(
        browser ? (localStorage.getItem('theme') || 'light') : 'light'
    );

    function toggle() {
        current = current === 'light' ? 'dark' : 'light';
        if (browser) {
            localStorage.setItem('theme', current);
            updateDocument();
        }
    }

    function updateDocument() {
        if (!browser) return;
        if (current === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }

    return {
        get current() { return current; },
        toggle,
        init: updateDocument
    };
}

export const theme = createTheme();
