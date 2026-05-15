<script lang="ts">
    import { Search, Settings, HelpCircle, Grid, List, LogOut, Cloud, Bell, User } from 'lucide-svelte';
    import { token } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { cn } from '$lib/utils';

    let { viewMode = $bindable('list'), onSearch = (query: string) => {} } = $props();

    let showSettings = $state(false);

    function logout() {
        token.set(null);
        goto('/login');
    }
</script>

<header class="h-20 border-b border-slate-100 flex items-center justify-between px-8 bg-white/80 backdrop-blur-md sticky top-0 z-40">
    <div class="flex items-center space-x-3">
        <div class="bg-indigo-600 p-2 rounded-xl shadow-lg shadow-indigo-200">
            <Cloud class="w-6 h-6 text-white" />
        </div>
        <span class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600 tracking-tight">
            SkyVault
        </span>
    </div>

    <div class="flex-1 max-w-xl mx-12">
        <div class="relative group">
            <span class="absolute inset-y-0 left-0 pl-4 flex items-center">
                <Search class="h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
            </span>
            <input 
                type="text" 
                placeholder="Search your vault..."
                class="block w-full pl-12 pr-4 py-2.5 bg-slate-100/50 border-2 border-transparent rounded-2xl focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-50 transition-all sm:text-sm outline-none"
                oninput={(e) => onSearch(e.currentTarget.value)}
            />
        </div>
    </div>

    <div class="flex items-center space-x-2">
        <button 
            onclick={() => viewMode = viewMode === 'list' ? 'grid' : 'list'} 
            class="p-2.5 hover:bg-slate-50 text-slate-500 hover:text-indigo-600 rounded-xl transition-all"
            title="Toggle View"
        >
            {#if viewMode === 'list'}
                <Grid class="w-5 h-5" />
            {:else}
                <List class="w-5 h-5" />
            {/if}
        </button>
        
        <button class="p-2.5 hover:bg-slate-50 text-slate-500 hover:text-indigo-600 rounded-xl transition-all relative">
            <Bell class="w-5 h-5" />
            <span class="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
        </button>

        <div class="relative">
            <button 
                onclick={() => showSettings = !showSettings}
                class={cn(
                    "p-2.5 hover:bg-slate-50 text-slate-500 hover:text-indigo-600 rounded-xl transition-all",
                    showSettings && "bg-indigo-50 text-indigo-600"
                )}
            >
                <Settings class="w-5 h-5" />
            </button>

            {#if showSettings}
                <div class="absolute right-0 mt-3 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 p-2 animate-in fade-in slide-in-from-top-2 duration-200">
                    <button class="w-full flex items-center space-x-3 px-3 py-2 hover:bg-slate-50 rounded-lg text-sm text-slate-600 transition-colors">
                        <User class="w-4 h-4" />
                        <span>Profile Settings</span>
                    </button>
                    <button class="w-full flex items-center space-x-3 px-3 py-2 hover:bg-slate-50 rounded-lg text-sm text-slate-600 transition-colors">
                        <Cloud class="w-4 h-4" />
                        <span>Storage Plan</span>
                    </button>
                    <div class="h-px bg-slate-100 my-2"></div>
                    <button 
                        onclick={logout}
                        class="w-full flex items-center space-x-3 px-3 py-2 hover:bg-rose-50 rounded-lg text-sm text-rose-600 transition-colors"
                    >
                        <LogOut class="w-4 h-4" />
                        <span>Sign Out</span>
                    </button>
                </div>
            {/if}
        </div>

        <div class="h-8 w-px bg-slate-200 mx-2"></div>

        <button class="flex items-center space-x-2 p-1 pl-1 pr-3 hover:bg-slate-50 rounded-2xl transition-all border border-transparent hover:border-slate-100">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-100">
                J
            </div>
            <span class="text-sm font-semibold text-slate-700">Jeswin</span>
        </button>
    </div>
</header>
