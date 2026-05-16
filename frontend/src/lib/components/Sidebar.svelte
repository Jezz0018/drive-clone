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
        Archive
    } from 'lucide-svelte';
    import { page } from '$app/stores';
    import { cn } from '$lib/utils';
    import { goto } from '$app/navigation';
    import { toasts } from '$lib/toasts';

    let { activeView = 'my-drive' } = $props();

    const menuItems = [
        { id: 'my-drive', label: 'My Files', icon: LayoutDashboard, path: '/' },
        { id: 'recent', label: 'Recent Files', icon: Clock, path: '/recent' },
        { id: 'starred', label: 'Favorites', icon: Star, path: '/starred' },
        { id: 'archive', label: 'Archived', icon: Archive, path: '/archive' },
        { id: 'shared', label: 'Shared with me', icon: Share2, path: '/shared' },
        { id: 'trash', label: 'Trash Bin', icon: Trash2, path: '/trash' },
    ];

    const categories = [
        { id: 'work', label: 'Work Projects', color: 'bg-indigo-500', path: '/category/work' },
        { id: 'personal', label: 'Personal', color: 'bg-emerald-500', path: '/category/personal' },
    ];
</script>

<aside class="w-80 bg-white dark:bg-slate-900 h-screen flex flex-col border-r border-slate-200/50 dark:border-slate-800/50 z-30 transition-colors duration-300">
    <!-- Navigation -->
    <nav class="flex-1 px-4 py-8 space-y-8 overflow-y-auto custom-scrollbar">        <!-- Main Section -->
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
                                ? "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400" 
                                : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-100"
                        )}
                    >
                        <div class="flex items-center space-x-3">
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
                    onclick={() => toasts.info('Category management coming soon')}
                    class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    <Plus class="w-3 h-3 text-slate-400" />
                </button>
            </div>
            <div class="space-y-1">
                {#each categories as cat}
                    <a 
                        href={cat.path}
                        class={cn(
                            "w-full flex items-center justify-between px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-2xl transition-all group text-left",
                            activeView === `cat-${cat.id}` && "bg-indigo-50 dark:bg-indigo-900/20"
                        )}
                    >
                        <div class="flex items-center space-x-3">
                            <div class={cn("w-2 h-2 rounded-full shadow-sm", cat.color)}></div>
                            <span class={cn(
                                "font-bold text-sm transition-colors",
                                activeView === `cat-${cat.id}` ? "text-indigo-600 dark:text-indigo-400" : "text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-slate-100"
                            )}>{cat.label}</span>
                        </div>
                    </a>
                {/each}
            </div>
        </div>

        <!-- Tools Section -->
        <div>
            <div class="px-4 mb-4">
                <span class="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Tools</span>
            </div>
            <div class="space-y-1 text-slate-600 dark:text-slate-400">
                <button 
                    onclick={() => toasts.info('Quick Actions coming soon')}
                    class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-2xl transition-all group"
                >
                    <Zap class="w-5 h-5 text-slate-400 dark:text-slate-500 group-hover:text-amber-500 transition-colors" />
                    <span class="font-bold text-sm tracking-tight">Quick Actions</span>
                </button>
                <button 
                    onclick={() => toasts.info('Privacy Scan coming soon')}
                    class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-2xl transition-all group"
                >
                    <ShieldCheck class="w-5 h-5 text-slate-400 dark:text-slate-500 group-hover:text-emerald-500 transition-colors" />
                    <span class="font-bold text-sm tracking-tight">Privacy Scan</span>
                </button>
            </div>
        </div>

        <!-- Account Section -->
        <div>
            <div class="px-4 mb-4">
                <span class="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Account</span>
            </div>
            <div class="space-y-1">
                <a 
                    href="/profile"
                    class={cn(
                        "flex items-center space-x-3 px-4 py-3.5 rounded-2xl transition-all group",
                        activeView === 'profile' 
                            ? "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400" 
                            : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                    )}
                >
                    <User class={cn("w-5 h-5 transition-colors", activeView === 'profile' ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500 group-hover:text-indigo-600")} />
                    <span class="font-bold text-sm tracking-tight">Profile Settings</span>
                </a>
            </div>
        </div>
    </nav>
</aside>

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
