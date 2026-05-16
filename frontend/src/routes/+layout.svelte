<script lang="ts">
    import './layout.css';
    import { onMount } from 'svelte';
    import { user, token } from '$lib/stores';
    import api from '$lib/api';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { theme } from '$lib/theme.svelte';
    import Toast from '$lib/components/Toast.svelte';
    import { Cloud } from 'lucide-svelte';

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
    <div class="flex items-center justify-center h-screen bg-slate-50 dark:bg-[#020617] transition-colors duration-500">
        <div class="flex flex-col items-center space-y-6">
            <div class="bg-indigo-600 p-5 rounded-[32px] shadow-2xl shadow-indigo-200 dark:shadow-none animate-pulse">
                <Cloud class="w-12 h-12 text-white" />
            </div>
            <div class="flex flex-col items-center">
                <h1 class="text-2xl font-black tracking-tighter text-slate-900 dark:text-white">
                    DRIVE <span class="text-indigo-600">X</span>
                </h1>
                <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.4em] mt-2">Initializing Drive</p>
            </div>
        </div>
    </div>
{:else}
    <div class="min-h-screen transition-colors duration-300">
        {@render children()}
    </div>
{/if}

<Toast />
