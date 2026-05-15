<script lang="ts">
    import './layout.css';
    import { onMount } from 'svelte';
    import { user, token } from '$lib/stores';
    import api from '$lib/api';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { theme } from '$lib/theme.svelte';
    import Toast from '$lib/components/Toast.svelte';

    let { children } = $props();
    let loading = $state(true);

    onMount(async () => {
        theme.init();
        if ($token) {
            try {
                // Fetch user info to verify token
                const response = await api.get('/auth/me'); // We might need to add this endpoint
                user.set(response.data);
                loading = false;
            } catch (e) {
                token.set(null);
                loading = false;
            }
        } else {
            loading = false;
        }
    });

    $effect(() => {
        if (!loading && !$token && $page.url.pathname !== '/login' && $page.url.pathname !== '/signup') {
            goto('/login');
        }
    });
</script>

<svelte:head>
    <title>DRIVE X | Your Secure Digital Space</title>
</svelte:head>

{#if loading}
    <div class="flex items-center justify-center h-screen bg-slate-50 dark:bg-[#0f172a] transition-colors duration-300">
        <div class="flex flex-col items-center space-y-4">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div>
            <p class="text-slate-500 dark:text-slate-400 font-bold animate-pulse">Initializing Vault...</p>
        </div>
    </div>
{:else}
    <div class="min-h-screen bg-slate-50 dark:bg-[#0f172a] transition-colors duration-300 text-slate-900 dark:text-slate-100">
        {@render children()}
    </div>
{/if}

<Toast />
