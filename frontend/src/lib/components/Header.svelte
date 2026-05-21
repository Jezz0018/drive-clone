<script lang="ts">
    import { Search, Settings, Grid, List, LogOut, Cloud, Bell, User, Sun, Moon, Aperture, Search as SearchIcon, Database, ShieldCheck, HelpCircle, Home } from 'lucide-svelte';
    import { token, user } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { cn } from '$lib/utils';
    import { theme } from '$lib/theme.svelte';
    import { fade, slide } from 'svelte/transition';
    import { toasts } from '$lib/toasts';

    let { viewMode = $bindable('list'), onSearch = (query: string) => {} } = $props();

    let showProfileMenu = $state(false);
    let showSettingsMenu = $state(false);
    let showNotifications = $state(false);

    function logout() {
        token.set(null);
        user.set(null);
        goto('/login');
    }

    function closeAllMenus() {
        showProfileMenu = false;
        showSettingsMenu = false;
        showNotifications = false;
    }
</script>

<svelte:window onclick={closeAllMenus} />

<header class="h-20 border-b border-slate-200/50 dark:border-slate-800/50 monochrome:border-white/10 flex items-center justify-between px-8 bg-white/70 dark:bg-slate-900/70 monochrome:bg-black backdrop-blur-xl sticky top-0 z-40 transition-all duration-300">
    <!-- Branding -->
    <button 
        class="flex items-center space-x-3 group cursor-pointer bg-transparent border-none p-0 focus:outline-none hover:scale-105 active:scale-95 transition-transform" 
        onclick={() => goto('/')}
        aria-label="Go to Dashboard"
    >
        <div class="bg-indigo-600 monochrome:bg-white p-2.5 rounded-2xl shadow-lg shadow-indigo-200 dark:shadow-indigo-900/20 monochrome:shadow-none group-hover:rotate-12 transition-transform duration-500">
            <Cloud class="w-6 h-6 text-white monochrome:text-black" />
        </div>
        <div class="flex flex-col -space-y-1">
            <span class="text-xl font-black tracking-tighter text-slate-900 dark:text-white monochrome:text-white group-hover:text-indigo-600 monochrome:group-hover:text-white/80 transition-colors">
                DRIVE <span class="text-indigo-600 monochrome:text-white">X</span>
            </span>
            <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Digital Storage</span>
        </div>
    </button>

    <!-- Home Button -->
    <button 
        onclick={() => goto('/')}
        class="ml-2 p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-500 dark:text-slate-400 monochrome:text-white/60 hover:text-indigo-600 dark:hover:text-indigo-400 monochrome:hover:text-white rounded-2xl transition-all hover-lift group active:scale-90"
        title="Back to Home"
    >
        <Home class="w-5 h-5 group-hover:scale-110 group-hover:rotate-6 transition-transform duration-300" />
    </button>

    <!-- Search Bar -->
    <div class="flex-1 max-w-2xl mx-12 hidden md:block">
        <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <SearchIcon class="h-5 w-5 text-slate-400 group-hover:text-indigo-400 dark:group-hover:text-indigo-300 monochrome:group-hover:text-white/80 group-hover:scale-110 group-hover:-rotate-12 group-focus-within:text-indigo-500 monochrome:group-focus-within:text-white group-focus-within:scale-125 group-focus-within:rotate-0 transition-all duration-500" />
            </div>
            <input 
                type="text" 
                placeholder="Search your secure drive..." 
                class="block w-full pl-12 pr-4 py-3 bg-slate-100/50 dark:bg-slate-800/50 monochrome:bg-white/5 border-2 border-transparent rounded-2xl hover:bg-slate-200/50 dark:hover:bg-slate-700/50 monochrome:hover:bg-white/10 hover:border-slate-200 dark:hover:border-slate-700 monochrome:hover:border-white/20 hover:scale-[1.01] focus:bg-white dark:focus:bg-slate-800 monochrome:focus:bg-white/10 focus:border-indigo-200 dark:focus:border-indigo-900/50 monochrome:focus:border-white focus:ring-8 focus:ring-indigo-50/50 dark:focus:ring-indigo-900/20 monochrome:focus:ring-white/5 transition-all duration-500 sm:text-sm outline-none text-slate-700 dark:text-slate-200 monochrome:text-white focus:scale-[1.02] shadow-sm hover:shadow-md focus:shadow-2xl focus:shadow-indigo-500/10 monochrome:focus:shadow-none"
                oninput={(e) => onSearch(e.currentTarget.value)}
            />
        </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center space-x-3">
        <!-- Theme Toggle -->
        <button 
            onclick={() => theme.toggle()}
            class="p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-500 dark:text-slate-400 monochrome:text-white/60 hover:text-indigo-600 dark:hover:text-indigo-400 monochrome:hover:text-white rounded-2xl transition-all hover:scale-110 active:scale-90 hover:rotate-45"
            title="Toggle Theme"
        >
            {#if theme.current === 'light'}
                <div in:fade><Sun class="w-5 h-5" /></div>
            {:else if theme.current === 'dark'}
                <div in:fade><Moon class="w-5 h-5" /></div>
            {:else}
                <div in:fade><Aperture class="w-5 h-5" /></div>
            {/if}
        </button>

        <!-- Settings Dropdown -->
        <div class="relative">
            <button
                onclick={(e) => {
                    e.stopPropagation();
                    showSettingsMenu = !showSettingsMenu;
                    showNotifications = false;
                    showProfileMenu = false;
                }}
                class="p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-500 dark:text-slate-400 monochrome:text-white/60 hover:text-indigo-600 dark:hover:text-indigo-400 monochrome:hover:text-white rounded-2xl transition-all relative group"
                title="Global Settings"
            >
                <Settings class="w-5 h-5 icon-rotate" />
            </button>

            {#if showSettingsMenu}
                <div 
                    class="absolute right-0 mt-4 w-72 bg-white dark:bg-slate-800 monochrome:bg-black rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-700 monochrome:border-white/20 p-2 z-50"
                    transition:slide
                    onclick={(e) => e.stopPropagation()}
                >
                    <div class="px-4 py-3 mb-2 border-b border-slate-50 dark:border-slate-700 monochrome:border-white/10">
                        <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 monochrome:text-white/40 uppercase tracking-widest">System Control</p>
                    </div>

                    <button 
                        onclick={() => { showSettingsMenu = false; goto('/profile'); }}
                        class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 monochrome:hover:bg-white/10 rounded-2xl text-sm font-bold text-slate-600 dark:text-slate-300 monochrome:text-white transition-colors"
                    >
                        <User class="w-4 h-4 text-indigo-500 monochrome:text-white" />
                        <span>Profile Settings</span>
                    </button>

                    <button 
                        onclick={() => { showSettingsMenu = false; goto('/storage'); }}
                        class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 monochrome:hover:bg-white/10 rounded-2xl text-sm font-bold text-slate-600 dark:text-slate-300 monochrome:text-white transition-colors"
                    >
                        <Database class="w-4 h-4 text-amber-500 monochrome:text-white" />
                        <span>Storage Settings</span>
                    </button>

                    <button 
                        onclick={() => { showSettingsMenu = false; goto('/security'); }}
                        class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 monochrome:hover:bg-white/10 rounded-2xl text-sm font-bold text-slate-600 dark:text-slate-300 monochrome:text-white transition-colors"
                    >
                        <ShieldCheck class="w-4 h-4 text-emerald-500 monochrome:text-white" />
                        <span>Security & Privacy</span>
                    </button>

                    <div class="h-px bg-slate-50 dark:bg-slate-700 monochrome:bg-white/10 my-2 mx-4"></div>

                    <button 
                        onclick={() => { showSettingsMenu = false; toasts.info('System manual initializing...'); }}
                        class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 monochrome:hover:bg-white/10 rounded-2xl text-sm font-bold text-slate-600 dark:text-slate-300 monochrome:text-white transition-colors"
                    >
                        <HelpCircle class="w-4 h-4 text-slate-400 monochrome:text-white/60" />
                        <span>Help & Documentation</span>
                    </button>
                </div>
            {/if}
            </div>

            <div class="relative">
            <button
                onclick={(e) => {
                    e.stopPropagation();
                    showNotifications = !showNotifications;
                    showSettingsMenu = false;
                    showProfileMenu = false;
                }}
                class="p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-500 dark:text-slate-400 monochrome:text-white/60 hover:text-indigo-600 dark:hover:text-indigo-400 monochrome:hover:text-white rounded-2xl transition-all relative group"
            >
                <Bell class="w-5 h-5 bell-shake" />
                <span class="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white dark:border-slate-900 monochrome:border-black"></span>
            </button>
            {#if showNotifications}
                <div 
                    class="absolute right-0 mt-4 w-80 bg-white dark:bg-slate-800 monochrome:bg-black rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-700 monochrome:border-white/20 p-4 animate-in fade-in slide-in-from-top-2 z-50"
                    transition:slide
                    onclick={(e) => e.stopPropagation()}
                >
                    <h3 class="font-bold text-slate-800 dark:text-white monochrome:text-white mb-3">Notifications</h3>
                    <div class="space-y-3">
                        <div class="flex items-start space-x-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-700/50 monochrome:hover:bg-white/10 rounded-xl transition-colors">
                            <div class="bg-indigo-100 dark:bg-indigo-900/30 monochrome:bg-white/10 p-2 rounded-lg">
                                <Cloud class="w-4 h-4 text-indigo-600 dark:text-indigo-400 monochrome:text-white" />
                            </div>
                            <div>
                                <p class="text-xs font-bold text-slate-800 dark:text-slate-200 monochrome:text-white">Welcome to DRIVE X!</p>
                                <p class="text-[10px] text-slate-500 dark:text-slate-400 monochrome:text-white/40">Start by uploading your first file.</p>
                            </div>
                        </div>
                    </div>
                </div>
            {/if}
        </div>

        <div class="h-8 w-px bg-slate-200 dark:bg-slate-800 monochrome:bg-white/10 mx-1"></div>

        <!-- Profile -->
        <div class="relative">
            <button 
                onclick={(e) => {
                    e.stopPropagation();
                    showProfileMenu = !showProfileMenu;
                    showNotifications = false;
                    showSettingsMenu = false;
                }}
                class={cn(
                    "flex items-center space-x-2 p-1.5 pl-1.5 pr-4 hover:bg-slate-100 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 rounded-[20px] transition-all border border-transparent group hover-lift",
                    showProfileMenu ? "bg-slate-100 dark:bg-slate-800 monochrome:bg-white/10 border-slate-200 dark:border-slate-700 monochrome:border-white/20" : "monochrome:text-white/60 hover:monochrome:text-white"
                )}
            >
                <div class="w-9 h-9 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 monochrome:from-white monochrome:to-gray-200 flex items-center justify-center text-white monochrome:text-black font-black shadow-md shadow-indigo-100 dark:shadow-none monochrome:shadow-none transition-transform group-hover:scale-110 group-hover:rotate-3">
                    {$user?.full_name?.charAt(0) || 'U'}
                </div>
                <div class="text-left hidden lg:block leading-tight">
                    <p class="text-sm font-bold text-slate-800 dark:text-white monochrome:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{$user?.full_name || 'User'}</p>
                    <p class="text-[10px] font-bold text-slate-400 monochrome:text-white/40 uppercase tracking-widest">{$user?.is_active ? 'Active User' : 'Inactive'}</p>
                </div>
            </button>

            {#if showProfileMenu}
                <div 
                    class="absolute right-0 mt-4 w-64 bg-white dark:bg-slate-800 monochrome:bg-black rounded-[28px] shadow-2xl border border-slate-100 dark:border-slate-700 monochrome:border-white/20 p-2 z-50"
                    transition:slide
                    onclick={(e) => e.stopPropagation()}
                >
                    <div class="px-4 py-3 mb-2">
                        <p class="text-xs font-bold text-slate-400 dark:text-slate-500 monochrome:text-white/40 uppercase tracking-widest">Personal Account</p>
                        <p class="text-sm font-bold text-slate-800 dark:text-white monochrome:text-white truncate">{$user?.email || 'Unknown Email'}</p>
                    </div>

                    <button 
                        onclick={logout}
                        class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-rose-50 dark:hover:bg-rose-900/20 monochrome:hover:bg-white/10 rounded-2xl text-sm font-bold text-rose-600 dark:text-rose-400 monochrome:text-white transition-colors"
                    >
                        <LogOut class="w-4 h-4" />
                        <span>Sign Out</span>
                    </button>
                </div>
            {/if}
        </div>
    </div>
</header>
