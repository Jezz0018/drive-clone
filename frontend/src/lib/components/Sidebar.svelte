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
        User,
        FolderPlus,
        UploadCloud,
        LogOut
    } from 'lucide-svelte';
    import { page } from '$app/stores';
    import { cn } from '$lib/utils';
    import { goto } from '$app/navigation';
    import { toasts } from '$lib/toasts';
    import CategoryManager from './CategoryManager.svelte';
    import StorageLiquid from './StorageLiquid.svelte';
    import api from '$lib/api';
    import { storageUsage, ui } from '$lib/stores';
    import { fade, slide, scale } from 'svelte/transition';

    let { activeView = 'my-drive' } = $props();
    let showCategoryManager = $state(false);
    let customCategories = $state<any[]>([]);
    let showCreateMenu = $state(false);

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
        <nav class="px-4 pt-8 pb-20 space-y-8">
            <!-- Create Button Section -->
            <div class="px-2">
                <div class="relative">
                    <button 
                        onclick={(e) => { e.stopPropagation(); showCreateMenu = !showCreateMenu; }}
                        class={cn(
                            "w-full flex items-center justify-center space-x-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-[24px] py-4 shadow-2xl shadow-indigo-500/30 dark:shadow-none transition-all active:scale-[0.98] font-black uppercase tracking-[0.2em] text-xs",
                            showCreateMenu && "ring-4 ring-indigo-500/10"
                        )}
                    >
                        <Plus class="w-5 h-5 stroke-[3px]" />
                        <span>Create New</span>
                    </button>

                    {#if showCreateMenu}
                        <div 
                            class="absolute left-0 top-full mt-4 w-full bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-[28px] shadow-2xl p-2 z-50 overflow-hidden"
                            transition:scale={{ duration: 150, start: 0.95 }}
                            onmouseleave={() => showCreateMenu = false}
                            onclick={(e) => e.stopPropagation()}
                        >
                            <button 
                                onclick={() => { ui.update(s => ({ ...s, showUploadModal: true, uploadType: 'folder' })); showCreateMenu = false; }}
                                class="w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all group"
                            >
                                <div class="bg-amber-100 dark:bg-amber-900/30 p-2 rounded-xl group-hover:scale-110 transition-transform">
                                    <FolderPlus class="w-4 h-4 text-amber-600 dark:text-amber-400" />
                                </div>
                                <span class="text-xs font-black uppercase tracking-widest">New Folder</span>
                            </button>
                            <button 
                                onclick={() => { ui.update(s => ({ ...s, showUploadModal: true, uploadType: 'file' })); showCreateMenu = false; }}
                                class="w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all group"
                            >
                                <div class="bg-indigo-100 dark:bg-indigo-900/30 p-2 rounded-xl group-hover:scale-110 transition-transform">
                                    <UploadCloud class="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                                </div>
                                <span class="text-xs font-black uppercase tracking-widest">Upload File</span>
                            </button>
                        </div>
                    {/if}
                </div>
            </div>

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
                                <Icon class={cn("w-5 h-5 transition-colors stroke-[2px]", activeView === item.id ? "text-indigo-600 dark:text-indigo-400" : "text-slate-500 dark:text-slate-500 group-hover:text-slate-700 dark:group-hover:text-slate-300")} />
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
                <div class="mx-2 bg-slate-200/50 dark:bg-slate-800/40 rounded-[32px] p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <div class="flex items-center justify-between mb-5">
                        <div class="flex items-center space-x-2">
                            <div class="p-2 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-100 dark:shadow-none">
                                <Database class="w-3.5 h-3.5 text-white" />
                            </div>
                            <span class="text-xs font-black text-slate-700 dark:text-slate-200 uppercase tracking-widest">DRIVE X</span>
                        </div>
                    </div>
                    
                    <StorageLiquid />
                    
                    <div class="flex justify-between items-center text-[9px] font-black uppercase tracking-widest mt-5 mb-5 px-1">
                        <span class="text-slate-500 dark:text-slate-400">{formatSize($storageUsage.used)}</span>
                        <span class="text-slate-300 dark:text-slate-600">|</span>
                        <span class="text-slate-400">{formatSize($storageUsage.limit)}</span>
                    </div>

                    <button 
                        onclick={() => toasts.info('Upgrade plans coming soon!')}
                        class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-[10px] font-black uppercase tracking-[0.2em] rounded-2xl transition-all active:scale-95 shadow-xl shadow-indigo-500/10 border border-transparent"
                    >
                        Upgrade Now
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
