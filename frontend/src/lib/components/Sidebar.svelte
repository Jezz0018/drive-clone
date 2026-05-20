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
            const response = await api.get('/items/', { params: { is_pinned: true } });
            pinnedItems = response.data;
        } catch (e) {}
    }

    async function fetchActivities() {
        try {
            const response = await api.get('/items/activity');
            activities = response.data;
        } catch (e) {}
    }

    async function fetchStorageUsage() {
        try {
            const response = await api.get(`/items/storage/usage?t=${Date.now()}`);
            storageUsage.set(response.data);
        } catch (e) {}
    }

    $effect(() => {
        if (!showCategoryManager) {
            fetchCustomCategories();
            fetchStorageUsage();
            fetchPinnedItems();
            fetchActivities();
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
        { id: 'my-drive', label: 'My Files', icon: LayoutDashboard, path: '/' },
        { id: 'recent', label: 'Recent Files', icon: Clock, path: '/recent' },
        { id: 'starred', label: 'Favorites', icon: Star, path: '/starred' },
        { id: 'trash', label: 'Trash Bin', icon: Trash2, path: '/trash' },
    ];

    const filterItems = [
        { id: 'images', label: 'Images', icon: ImageIcon, color: 'text-rose-500', bg: 'bg-rose-50 dark:bg-rose-900/20' },
        { id: 'docs', label: 'Documents', icon: FileText, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/20' },
        { id: 'video', label: 'Videos', icon: Video, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20' },
        { id: 'audio', label: 'Audio', icon: Music, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-900/20' },
        { id: 'zip', label: 'Archives', icon: Box, color: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-900/20' },
    ];
</script>

<div class="flex h-screen overflow-hidden">
    <!-- Workspace Switcher (Far Left) -->
    <aside class="w-20 bg-slate-900 dark:bg-[#020617] h-full flex flex-col items-center py-8 space-y-6 shrink-0 border-r border-white/5">
        <div class="w-12 h-12 bg-indigo-600 rounded-[18px] flex items-center justify-center text-white mb-4 shadow-2xl shadow-indigo-500/40">
            <Cloud class="w-7 h-7 stroke-[2.5px]" />
        </div>
        
        <div class="flex-1 w-full flex flex-col items-center space-y-4">
            {#each workspaces as ws}
                <button 
                    onclick={() => activeWorkspace = ws.id}
                    class={cn(
                        "w-12 h-12 rounded-[18px] flex items-center justify-center transition-all duration-300 group relative",
                        activeWorkspace === ws.id ? "bg-white/10 text-white scale-110" : "text-slate-500 hover:bg-white/5 hover:text-slate-300"
                    )}
                    title={ws.label}
                >
                    <svelte:component this={ws.icon} class="w-6 h-6" />
                    {#if activeWorkspace === ws.id}
                        <div class="absolute -left-4 w-1.5 h-6 bg-indigo-500 rounded-r-full" in:fade></div>
                    {/if}
                </button>
            {/each}
            
            <div class="w-8 h-px bg-white/10 my-2"></div>
            
            <button class="w-12 h-12 rounded-[18px] border-2 border-dashed border-white/10 flex items-center justify-center text-slate-500 hover:border-white/20 hover:text-slate-300 transition-all">
                <Plus class="w-5 h-5" />
            </button>
        </div>

        <button class="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white transition-all overflow-hidden border border-white/5">
            <User class="w-6 h-6" />
        </button>
    </aside>

    <!-- Main Sidebar -->
    <aside class="w-72 bg-white dark:bg-slate-900 h-full flex flex-col border-r border-slate-200/50 dark:border-slate-800/50 z-30 transition-colors duration-300 overflow-hidden">
        <div class="flex-1 overflow-y-auto custom-scrollbar">
            <nav class="px-4 pt-8 pb-12 space-y-8">
                <!-- Create Button -->
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
                                class="absolute left-0 top-full mt-4 w-full bg-white dark:bg-slate-950 border border-slate-100 dark:border-slate-800 rounded-[28px] shadow-2xl p-2 z-50 overflow-hidden"
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

                <!-- Dashboard -->
                <div>
                    <div class="px-4 mb-3 flex items-center justify-between font-black text-[10px] text-slate-400 uppercase tracking-widest">
                        Dashboard
                    </div>
                    <div class="space-y-1">
                        {#each menuItems as item}
                            {@const Icon = item.icon}
                            <a href={item.path} class={cn("flex items-center space-x-3 px-4 py-3 rounded-2xl transition-all", activeView === item.id ? "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 font-bold" : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-100")}>
                                <Icon class="w-5 h-5 stroke-[2px]" />
                                <span class="text-sm tracking-tight">{item.label}</span>
                            </a>
                        {/each}
                    </div>
                </div>

                <!-- Quick Filters -->
                <div>
                    <div class="px-4 mb-3 font-black text-[10px] text-slate-400 uppercase tracking-widest">
                        Quick Filters
                    </div>
                    <div class="space-y-1">
                        {#each filterItems as filter}
                            <button 
                                class={cn(
                                    "w-full flex items-center space-x-3 px-4 py-2.5 rounded-2xl transition-all group",
                                    $ui.mimeFilter === filter.id 
                                        ? "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 font-bold" 
                                        : "hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                                )}
                                onclick={() => {
                                    const newFilter = $ui.mimeFilter === filter.id ? undefined : filter.id;
                                    ui.update(s => ({ ...s, mimeFilter: newFilter }));
                                }}
                            >
                                <div class={cn("p-1.5 rounded-lg transition-transform group-hover:scale-110", filter.bg)}>
                                    <svelte:component this={filter.icon} class={cn("w-3.5 h-3.5", filter.color)} />
                                </div>
                                <span class="text-xs font-bold">{filter.label}</span>
                            </button>
                        {/each}
                    </div>
                </div>

                <!-- Pinned Items -->
                {#if pinnedItems.length > 0}
                    <div>
                        <div class="px-4 mb-3 flex items-center space-x-2 font-black text-[10px] text-slate-400 uppercase tracking-widest">
                            <Pin class="w-3 h-3" /> <span>Quick Access</span>
                        </div>
                        <div class="space-y-1">
                            {#each pinnedItems as item}
                                <button class="w-full flex items-center space-x-3 px-4 py-2.5 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-400 transition-all text-left">
                                    <div class={cn("p-1.5 rounded-lg", item.is_folder ? "bg-amber-100 dark:bg-amber-900/30" : "bg-indigo-100 dark:bg-indigo-900/30")}>
                                        <svelte:component this={item.is_folder ? Folder : FileIcon} class="w-3.5 h-3.5" />
                                    </div>
                                    <span class="text-xs font-bold truncate">{item.name}</span>
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Activity Feed -->
                {#if activities.length > 0}
                    <div>
                        <div class="px-4 mb-4 flex items-center space-x-2 font-black text-[10px] text-slate-400 uppercase tracking-widest">
                            <ActivityIcon class="w-3 h-3" /> <span>Live Activity</span>
                        </div>
                        <div class="px-4 space-y-4">
                            {#each activities as act}
                                <div class="flex items-start space-x-3 relative group">
                                    <div class="w-1 h-full absolute left-[7px] top-6 bg-slate-100 dark:bg-slate-800 rounded-full group-last:hidden"></div>
                                    <div class="w-4 h-4 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center shrink-0 mt-0.5 z-10 border-2 border-white dark:border-slate-900">
                                        <div class="w-1.5 h-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400"></div>
                                    </div>
                                    <div class="min-w-0">
                                        <p class="text-[10px] font-bold text-slate-700 dark:text-slate-200 truncate leading-tight">{act.action === 'upload' ? 'Uploaded' : 'Created'} {act.item_name}</p>
                                        <p class="text-[8px] font-black text-slate-400 uppercase tracking-widest mt-0.5">{new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Storage Widget -->
                <div class="pt-8 border-t border-slate-200 dark:border-slate-800">
                    <div class="mx-2 bg-slate-200/50 dark:bg-slate-800/40 rounded-[32px] p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
                        <StorageLiquid />
                        <div class="flex justify-between items-center text-[9px] font-black uppercase tracking-widest mt-5 px-1">
                            <span class="text-slate-500 dark:text-slate-400">{formatSize($storageUsage.used)}</span>
                            <span class="text-slate-400">of {formatSize($storageUsage.limit)}</span>
                        </div>
                    </div>
                </div>
            </nav>
        </div>
    </aside>
</div>

<style>
    @reference "../../routes/layout.css";
    .custom-scrollbar::-webkit-scrollbar { width: 4px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
    .custom-scrollbar::-webkit-scrollbar-thumb { @apply bg-slate-200 dark:bg-slate-800 rounded-full; }
</style>
