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
        LogOut,
        Image as ImageIcon,
        FileText,
        Video,
        Music,
        Box,
        File as FileIcon,
        Activity as ActivityIcon,
        ChevronRight,
        Pin,
        Cloud,
        Briefcase,
        Globe
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
    let pinnedItems = $state<any[]>([]);
    let activities = $state<any[]>([]);
    let showCreateMenu = $state(false);
    let activeWorkspace = $state('personal');

    async function fetchCustomCategories() {
        try {
            const response = await api.get('/categories/');
            customCategories = response.data;
        } catch (e) {}
    }

    async function fetchPinnedItems() {
        try {
            const response = await api.get('/items/', { params: { is_pinned: true, t: Date.now() } });
            pinnedItems = response.data;
        } catch (e) {}
    }

    async function fetchActivities() {
        try {
            const response = await api.get('/items/activity');
            activities = response.data;
        } catch (e) {}
    }

    function navigateToItem(item: any) {
        if (item.is_folder) {
            goto(`/?folder=${item.id}`);
        } else {
            const path = item.parent_id ? `/?folder=${item.parent_id}` : '/';
            goto(path);
            toasts.info(`Opening location for ${item.name}`);
        }
    }

    async function fetchStorageUsage() {
        try {
            const response = await api.get(`/items/storage/usage?t=${Date.now()}`);
            storageUsage.set(response.data);
        } catch (e) {}
    }

    $effect(() => {
        const _ = $ui.sidebarRefreshCounter;
        fetchCustomCategories();
        fetchStorageUsage();
        fetchPinnedItems();
        fetchActivities();
    });

    $effect(() => {
        if (activeWorkspace === 'personal') {
            ui.update(s => ({ ...s, mimeFilter: undefined }));
        } else if (activeWorkspace === 'public') {
            ui.update(s => ({ ...s, mimeFilter: 'public' }));
        } else if (activeWorkspace === 'work') {
            ui.update(s => ({ ...s, mimeFilter: 'shared' }));
        }
    });

    function formatSize(bytes?: number) {
        if (!bytes) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    const workspaces = [
        { id: 'personal', icon: Cloud, label: 'Personal' },
        { id: 'work', icon: Briefcase, label: 'Work' },
        { id: 'public', icon: Globe, label: 'Public' },
    ];

    const menuItems = [
        { id: 'activities', label: 'Activities', icon: ActivityIcon, path: '/activities' },
        { id: 'my-drive', label: 'My Drive', icon: LayoutDashboard, path: '/' },
        { id: 'recent', label: 'Recent', icon: Clock, path: '/recent' },
        { id: 'starred', label: 'Favorites', icon: Star, path: '/starred' },
        { id: 'archive', label: 'Archive', icon: Archive, path: '/archive' },
        { id: 'trash', label: 'Trash', icon: Trash2, path: '/trash' },
    ];

    const filterItems = [
        { id: 'images', label: 'Images', icon: ImageIcon, color: 'text-rose-500', bg: 'bg-rose-50 dark:bg-rose-900/20 monochrome:bg-white/5' },
        { id: 'docs', label: 'Documents', icon: FileText, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/20 monochrome:bg-white/5' },
        { id: 'video', label: 'Videos', icon: Video, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20 monochrome:bg-white/5' },
        { id: 'audio', label: 'Audio', icon: Music, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-900/20 monochrome:bg-white/5' },
        { id: 'zip', label: 'Archives', icon: Box, color: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-900/20 monochrome:bg-white/5' },
    ];
</script>

<div class="flex h-full overflow-hidden transition-colors duration-500">
    <!-- Workspace Switcher (Far Left) -->
    <aside class="w-20 bg-slate-100/50 dark:bg-[#020617] monochrome:bg-black h-full flex flex-col items-center py-8 space-y-6 shrink-0 border-r border-slate-200/50 dark:border-white/5 monochrome:border-white/10">
        <div class="flex-1 w-full flex flex-col items-center space-y-4">
            {#each workspaces as ws}
                <button 
                    onclick={() => activeWorkspace = ws.id}
                    class={cn(
                        "w-14 h-14 rounded-[18px] flex flex-col items-center justify-center transition-all duration-300 group relative hover-lift",
                        activeWorkspace === ws.id 
                            ? "bg-indigo-600 dark:bg-white/10 monochrome:bg-white text-white monochrome:text-black scale-110" 
                            : "text-slate-400 dark:text-slate-500 monochrome:text-white/40 hover:bg-indigo-50 dark:hover:bg-white/5 monochrome:hover:bg-white/10 hover:text-indigo-600 dark:hover:text-slate-300 monochrome:hover:text-white"
                    )}
                    title={ws.label}
                >
                    <svelte:component this={ws.icon} class="w-5 h-5 mb-1 icon-bounce" />
                    <span class="text-[7px] font-black uppercase tracking-tighter opacity-70 group-hover:opacity-100 transition-opacity">{ws.label}</span>
                    {#if activeWorkspace === ws.id}
                        <div class="absolute -left-3 w-1 h-6 bg-indigo-500 monochrome:bg-white rounded-r-full" in:fade></div>
                    {/if}
                </button>
            {/each}
            
            <div class="w-8 h-px bg-slate-200 dark:bg-white/10 monochrome:bg-white/20 my-2"></div>
            
            <button class="w-12 h-12 rounded-[18px] border-2 border-dashed border-slate-200 dark:border-white/10 monochrome:border-white/10 flex items-center justify-center text-slate-400 hover:border-indigo-300 hover:text-indigo-600 monochrome:hover:text-white monochrome:hover:border-white transition-all">
                <Plus class="w-5 h-5" />
            </button>
        </div>
    </aside>

    <!-- Main Sidebar -->
    <aside class="w-72 bg-white dark:bg-slate-900 monochrome:bg-black h-full flex flex-col border-r border-slate-200/50 dark:border-slate-800/50 monochrome:border-white/10 z-30 overflow-hidden">
        <div class="flex-1 overflow-y-auto custom-scrollbar">
            <nav class="px-4 pt-8 pb-12 space-y-8">
                <!-- Create Button -->
                <div class="px-2">
                    <div class="relative group/create">
                        <button 
                            onclick={(e) => { e.stopPropagation(); showCreateMenu = !showCreateMenu; }}
                            class={cn(
                                "w-full flex items-center justify-center space-x-3 bg-indigo-600 hover:bg-indigo-700 monochrome:bg-white monochrome:hover:bg-gray-100 text-white monochrome:text-black rounded-[24px] py-4 shadow-2xl shadow-indigo-500/30 dark:shadow-none monochrome:shadow-none transition-all active:scale-[0.98] font-black uppercase tracking-[0.2em] text-xs hover-lift group",
                                showCreateMenu && "ring-4 ring-indigo-500/10 monochrome:ring-white/10"
                            )}
                        >
                            <Plus class={cn("w-5 h-5 stroke-[3px] icon-rotate", showCreateMenu && "rotate-45")} />
                            <span>Create New</span>
                        </button>

                        {#if showCreateMenu}
                            <div 
                                class="absolute left-0 top-full mt-4 w-full bg-white dark:bg-slate-950 monochrome:bg-black border border-slate-100 dark:border-slate-800 monochrome:border-white/20 rounded-[28px] shadow-2xl p-2 z-50 overflow-hidden"
                                transition:scale={{ duration: 150, start: 0.95 }}
                                onmouseleave={() => showCreateMenu = false}
                                onclick={(e) => e.stopPropagation()}
                            >
                                <button 
                                    onclick={() => { ui.update(s => ({ ...s, showUploadModal: true, uploadType: 'folder' })); showCreateMenu = false; }}
                                    class="w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-700 dark:text-slate-300 monochrome:text-white transition-all group"
                                >
                                    <div class="bg-amber-100 dark:bg-amber-900/30 monochrome:bg-white/10 p-2 rounded-xl group-hover:scale-110 transition-transform">
                                        <FolderPlus class="w-4 h-4 text-amber-600 dark:text-amber-400 monochrome:text-white" />
                                    </div>
                                    <span class="text-xs font-black uppercase tracking-widest">New Folder</span>
                                </button>
                                <button 
                                    onclick={() => { ui.update(s => ({ ...s, showUploadModal: true, uploadType: 'file' })); showCreateMenu = false; }}
                                    class="w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-700 dark:text-slate-300 monochrome:text-white transition-all group"
                                >
                                    <div class="bg-indigo-100 dark:bg-indigo-900/30 monochrome:bg-white/10 p-2 rounded-xl group-hover:scale-110 transition-transform">
                                        <UploadCloud class="w-4 h-4 text-indigo-600 dark:text-indigo-400 monochrome:text-white" />
                                    </div>
                                    <span class="text-xs font-black uppercase tracking-widest">Upload File</span>
                                </button>
                            </div>
                        {/if}
                    </div>
                </div>

                <!-- Dashboard -->
                <div>
                    <div class="px-4 mb-3 font-black text-[10px] text-slate-400 dark:text-slate-500 monochrome:text-white/40 uppercase tracking-widest">
                        Dashboard
                    </div>
                    <div class="space-y-1">
                        {#each menuItems as item}
                            {@const Icon = item.icon}
                            <a 
                                href={item.path} 
                                class={cn(
                                    "flex items-center space-x-3 px-4 py-3 rounded-2xl transition-all hover-lift", 
                                    activeView === item.id 
                                        ? "bg-indigo-50 dark:bg-indigo-900/20 monochrome:bg-white text-indigo-600 dark:text-indigo-400 monochrome:text-black font-bold" 
                                        : "text-slate-500 dark:text-slate-400 monochrome:text-white/60 hover:bg-slate-50 dark:hover:bg-slate-800/50 monochrome:hover:bg-white/10 hover:text-slate-900 dark:hover:text-slate-100 monochrome:hover:text-white"
                                )}
                            >
                                <Icon class="w-5 h-5 stroke-[2px] icon-bounce" />
                                <span class="text-sm tracking-tight">{item.label}</span>
                            </a>
                        {/each}
                    </div>
                </div>

                <!-- Quick Filters -->
                <div>
                    <div class="px-4 mb-3 font-black text-[10px] text-slate-400 dark:text-slate-500 monochrome:text-white/40 uppercase tracking-widest">
                        Quick Filters
                    </div>
                    <div class="space-y-1">
                        {#each filterItems as filter}
                            <button 
                                class={cn(
                                    "w-full flex items-center space-x-3 px-4 py-2.5 rounded-2xl transition-all group hover-lift",
                                    $ui.mimeFilter === filter.id 
                                        ? "bg-indigo-50 dark:bg-indigo-900/20 monochrome:bg-white text-indigo-600 dark:text-indigo-400 monochrome:text-black font-bold" 
                                        : "hover:bg-slate-50 dark:hover:bg-slate-800/50 monochrome:hover:bg-white/10 text-slate-500 dark:text-slate-400 monochrome:text-white/60 hover:text-slate-900 dark:hover:text-white monochrome:hover:text-white"
                                )}
                                onclick={() => {
                                    const newFilter = $ui.mimeFilter === filter.id ? undefined : filter.id;
                                    ui.update(s => ({ ...s, mimeFilter: newFilter }));
                                }}
                            >
                                <div class={cn("p-1.5 rounded-lg transition-transform icon-bounce", filter.bg)}>
                                    <svelte:component this={filter.icon} class={cn("w-3.5 h-3.5", filter.color)} />
                                </div>
                                <span class="text-xs font-bold">{filter.label}</span>
                            </button>
                        {/each}
                    </div>
                </div>

                <!-- Pinned Items -->
                <div>
                    <div class="px-4 mb-3 flex items-center space-x-2 font-black text-[10px] text-slate-400 dark:text-slate-500 monochrome:text-white/40 uppercase tracking-widest">
                        <Pin class="w-3 h-3" /> <span>Quick Access</span>
                    </div>
                    <div class="space-y-1">
                        {#each pinnedItems as item}
                            {@const Icon = item.is_folder ? Folder : FileIcon}
                            <button 
                                onclick={() => navigateToItem(item)}
                                class="w-full flex items-center space-x-3 px-4 py-2.5 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-800/50 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-400 monochrome:text-white transition-all text-left group"
                            >
                                <div class={cn("p-1.5 rounded-lg transition-transform group-hover:scale-110", item.is_folder ? "bg-amber-100 dark:bg-amber-900/30 monochrome:bg-white/10" : "bg-indigo-100 dark:bg-indigo-900/30 monochrome:bg-white/10")}>
                                    <Icon class={cn("w-3.5 h-3.5", item.is_folder ? "text-amber-600 monochrome:text-white" : "text-indigo-600 monochrome:text-white")} />
                                </div>
                                <span class="text-xs font-bold truncate group-hover:text-slate-900 dark:group-hover:text-white monochrome:group-hover:text-white transition-colors">{item.name}</span>
                            </button>
                        {:else}
                            <div class="px-4 py-4 text-center">
                                <p class="text-[10px] font-bold text-slate-300 dark:text-slate-600 monochrome:text-white/20 uppercase tracking-widest">No Pinned Items</p>
                            </div>
                        {/each}
                    </div>
                </div>

                <!-- Activity Feed -->
                {#if activities.length > 0}
                    <div>
                        <div class="px-4 mb-4 flex items-center space-x-2 font-black text-[10px] text-slate-400 dark:text-slate-500 monochrome:text-white/40 uppercase tracking-widest">
                            <ActivityIcon class="w-3 h-3" /> <span>Live Activity</span>
                        </div>
                        <div class="px-4 space-y-4">
                            {#each activities as act}
                                <div class="flex items-start space-x-3 relative group">
                                    <div class="w-1 h-full absolute left-[7px] top-6 bg-slate-100 dark:bg-slate-800 monochrome:bg-white/10 rounded-full group-last:hidden"></div>
                                    <div class="w-4 h-4 rounded-full bg-indigo-100 dark:bg-indigo-900/40 monochrome:bg-white/20 flex items-center justify-center shrink-0 mt-0.5 z-10 border-2 border-white dark:border-slate-900 monochrome:border-white/10">
                                        <div class="w-1.5 h-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400 monochrome:bg-white"></div>
                                    </div>
                                    <div class="min-w-0">
                                        <p class="text-[10px] font-bold text-slate-700 dark:text-slate-200 monochrome:text-white truncate leading-tight">{act.action === 'upload' ? 'Uploaded' : 'Created'} {act.item_name}</p>
                                        <p class="text-[8px] font-black text-slate-400 dark:text-slate-500 monochrome:text-white/40 uppercase tracking-widest mt-0.5">{new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Storage Widget -->
                <div class="pt-8 border-t border-slate-200 dark:border-slate-800 monochrome:border-white/10">
                    <div class="mx-2 bg-slate-200/50 dark:bg-slate-800/40 monochrome:bg-white/5 rounded-[32px] p-5 border border-slate-200 dark:border-slate-800 monochrome:border-white/10 shadow-sm">
                        <StorageLiquid />
                        <div class="flex justify-between items-center text-[9px] font-black uppercase tracking-widest mt-5 px-1">
                            <span class="text-slate-500 dark:text-slate-400 monochrome:text-white/60">{formatSize($storageUsage.used)}</span>
                            <span class="text-slate-400 monochrome:text-white/40">of {formatSize($storageUsage.limit)}</span>
                        </div>
                    </div>
                </div>
            </nav>
        </div>
    </aside>
</div>

{#if showCategoryManager}
    <CategoryManager onclose={() => showCategoryManager = false} />
{/if}

<style>
    @reference "../../routes/layout.css";

    .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        @apply bg-slate-200 dark:bg-slate-800 monochrome:bg-white/20 rounded-full;
    }
</style>
