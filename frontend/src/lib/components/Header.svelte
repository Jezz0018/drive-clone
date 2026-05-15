<script lang="ts">
    import { Search, Settings, HelpCircle, Grid, List, LogOut } from 'lucide-svelte';
    import { token } from '$lib/stores';
    import { goto } from '$app/navigation';

    export let viewMode = 'list';
    export let onSearch = (query: string) => {};

    function logout() {
        token.set(null);
        goto('/login');
    }
</script>

<header class="h-16 border-b border-gray-200 flex items-center justify-between px-4 bg-white">
    <div class="flex items-center space-x-2">
        <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg" alt="Logo" class="w-8 h-8" />
        <span class="text-xl font-medium text-gray-700">Drive</span>
    </div>

    <div class="flex-1 max-w-2xl mx-8">
        <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center">
                <Search class="h-5 w-5 text-gray-400" />
            </span>
            <input 
                type="text" 
                placeholder="Search in Drive"
                class="block w-full pl-10 pr-3 py-2 bg-gray-100 border border-transparent rounded-lg focus:bg-white focus:border-gray-200 focus:ring-0 sm:text-sm"
                on:input={(e) => onSearch(e.currentTarget.value)}
            />
        </div>
    </div>

    <div class="flex items-center space-x-4">
        <button on:click={() => viewMode = viewMode === 'list' ? 'grid' : 'list'} class="p-2 hover:bg-gray-100 rounded-full">
            {#if viewMode === 'list'}
                <Grid class="w-6 h-6 text-gray-600" />
            {:else}
                <List class="w-6 h-6 text-gray-600" />
            {/if}
        </button>
        <button class="p-2 hover:bg-gray-100 rounded-full">
            <Settings class="w-6 h-6 text-gray-600" />
        </button>
        <button on:click={logout} class="p-2 hover:bg-gray-100 rounded-full text-red-600" title="Logout">
            <LogOut class="w-6 h-6" />
        </button>
        <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-medium">
            J
        </div>
    </div>
</header>
