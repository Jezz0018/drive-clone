<script lang="ts">
    import './layout.css';
    import { onMount } from 'svelte';
    import { user, token } from '$lib/stores';
    import api from '$lib/api';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    let { children } = $props();
    let loading = $state(true);

    onMount(async () => {
        if ($token) {
            try {
                // We should add a /users/me endpoint to the backend later
                // For now, we'll just assume token is valid or will fail on first request
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

{#if loading}
    <div class="flex items-center justify-center h-screen">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
{:else}
    {@render children()}
{/if}
