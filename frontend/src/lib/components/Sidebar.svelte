<script lang="ts">
    import { 
        Home, 
        Folder, 
        Star, 
        Clock, 
        Trash2, 
        HardDrive,
        Plus,
        Database,
        Users,
        Share2,
        ShieldCheck,
        Layers,
        Zap,
        LayoutDashboard,
        Archive,
        User
    } from 'lucide-svelte';
    import { page } from '$app/stores';
    import { cn } from '$lib/utils';
    import { goto } from '$app/navigation';
    import { toasts } from '$lib/toasts';
    import CategoryManager from './CategoryManager.svelte';
    import api from '$lib/api';
    import { storageUsage } from '$lib/stores';

    let { activeView = 'my-drive' } = $props();
    let showCategoryManager = $state(false);
    let customCategories = $state<any[]>([]);

    async function fetchCustomCategories() {
        try {
            const response = await api.get('/categories/');
            customCategories = response.data;
        } catch (e) {
            // Silently fail
        }
    }

    async function fetchStorageUsage() {
        try {
            const response = await api.get(`/items/storage/usage?t=${Date.now()}`);
            storageUsage.set(response.data);
        } catch (e) {
            // Silently fail
        }
    }

    $effect(() => {
        if (!showCategoryManager) {
            fetchCustomCategories();
            fetchStorageUsage();
        }
    });

    function formatSize(bytes?: number) {
        if (!bytes) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    const menuItems = [
        { id: 'my-drive', label: 'My Files', icon: LayoutDashboard, path: '/' },
        { id: 'recent', label: 'Recent Files', icon: Clock, path: '/recent' },
        { id: 'starred', label: 'Favorites', icon: Star, path: '/starred' },
        { id: 'archive', label: 'Archived', icon: Archive, path: '/archive' },
        { id: 'shared', label: 'Shared', icon: Users, path: '/shared' },
        { id: 'trash', label: 'Trash Bin', icon: Trash2, path: '/trash' },
    ];
</script>

<aside class="w-80 bg-slate-100 dark:bg-slate-900 h-screen flex flex-col border-r border-slate-200/50 dark:border-slate-800/50 z-30 transition-colors duration-300 overflow-hidden">
    <!-- Navigation Wrapper -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
        <nav class="px-4 py-8 space-y-8">
            <!-- Main Section -->
            <div>
                <div class="px-4 mb-4">
                    <span class="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Dashboard</span>
                </div>
                <div class="space-y-1">
                    {#each menuItems as item}
                        {@const Icon = item.icon}
                        <a 
                            href={item.path}
                            class={cn(
                                "flex items-center justify-between px-4 py-3.5 rounded-2xl transition-all group relative",
                                activeView === item.id 
                                    ? "bg-indigo-100 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400" 
                                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-100"
                            )}
                        >                            <div class="flex items-center space-x-3">
                                <Icon class={cn("w-5 h-5 transition-colors stroke-[2px]", activeView === item.id ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300")} />
                                <span class="font-bold text-sm tracking-tight">{item.label}</span>
                            </div>
                            {#if activeView === item.id}
                                <div class="absolute right-2 w-1.5 h-1.5 bg-indigo-600 dark:bg-indigo-400 rounded-full shadow-lg shadow-indigo-200 dark:shadow-indigo-900/50"></div>
                            {/if}
                        </a>
                    {/each}
                </div>
            </div>

            <!-- Categories Section -->
            <div>
                <div class="px-4 mb-4 flex items-center justify-between">
                    <span class="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Categories</span>
                    <button 
                        onclick={() => showCategoryManager = true}
                        class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        <Plus class="w-3 h-3 text-slate-400" />
                    </button>
                </div>
                <div class="space-y-1">
                    {#each customCategories as cat}
                        <a 
                            href={`/category/${cat.name.toLowerCase()}`}
                            class={cn(
                                "w-full flex items-center justify-between px-4 py-3 hover:bg-slate-200 dark:hover:bg-slate-800/50 rounded-2xl transition-all group text-left",
                                activeView === `cat-${cat.name.toLowerCase()}` && "bg-indigo-100 dark:bg-indigo-900/20"
                            )}
                        >
                            <div class="flex items-center space-x-3">
                                <div class={cn("w-2 h-2 rounded-full shadow-sm", cat.color)}></div>
                                <span class={cn(
                                    "font-bold text-sm transition-colors",
                                    activeView === `cat-${cat.name.toLowerCase()}` ? "text-indigo-600 dark:text-indigo-400" : "text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-slate-100"
                                )}>{cat.name}</span>
                            </div>
                        </a>
                    {/each}
                </div>
            </div>

            <!-- Storage Section (Now inside the scrollable container) -->
            <div class="pt-8 border-t border-slate-200 dark:border-slate-800">
                <div class="mb-4 px-4">
                    <span class="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Storage Usage</span>
                </div>
                <div class="mx-2 bg-slate-200/50 dark:bg-slate-800/40 rounded-3xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center space-x-2">
                            <div class="p-2 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-100 dark:shadow-none">
                                <Database class="w-3.5 h-3.5 text-white" />
                            </div>
                            <span class="text-xs font-black text-slate-700 dark:text-slate-200">Personal Cloud</span>
                        </div>
                        <span class="text-[10px] font-black text-indigo-600 dark:text-indigo-400">
                            {Math.round(($storageUsage.used / $storageUsage.limit) * 100)}%
                        </span>
                    </div>
                    
                    <div class="h-2 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden mb-4">
                        <div 
                            class="h-full bg-indigo-600 dark:bg-indigo-500 rounded-full transition-all duration-1000"
                            style="width: {($storageUsage.used / $storageUsage.limit) * 100}%"
                        ></div>
                    </div>
                    
                    <div class="flex justify-between items-center text-[10px] font-bold mb-5">
                        <span class="text-slate-500 dark:text-slate-400">{formatSize($storageUsage.used)} used</span>
                        <span class="text-slate-400">of {formatSize($storageUsage.limit)}</span>
                    </div>

                    <button 
                        onclick={() => toasts.info('Upgrade plans coming soon!')}
                        class="w-full py-2.5 bg-indigo-50 dark:bg-indigo-600 hover:bg-indigo-100 dark:hover:bg-indigo-700 text-indigo-600 dark:text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-all active:scale-95 shadow-sm border border-indigo-200 dark:border-transparent"
                    >
                        Upgrade Plan
                    </button>
                </div>
            </div>
        </nav>
    </div>
</aside>

{#if showCategoryManager}
    <CategoryManager onclose={() => showCategoryManager = false} />
{/if}

<style>
    @reference "tailwindcss";

    .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        @apply bg-slate-200 dark:bg-slate-800 rounded-full;
    }
</style>
