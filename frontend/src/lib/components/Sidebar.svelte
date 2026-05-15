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
        LayoutDashboard
    } from 'lucide-svelte';
    import { page } from '$app/stores';
    import { cn } from '$lib/utils';
    import { goto } from '$app/navigation';

    let { activeView = 'my-drive' } = $props();

    const menuItems = [
        { id: 'my-drive', label: 'All Assets', icon: LayoutDashboard, path: '/' },
        { id: 'recent', label: 'Recent Files', icon: Clock, path: '/recent' },
        { id: 'starred', label: 'Favorites', icon: Star, path: '/starred' },
        { id: 'shared', label: 'Shared with me', icon: Share2, path: '/shared' },
        { id: 'trash', label: 'Trash Bin', icon: Trash2, path: '/trash' },
    ];

    const categories = [
        { label: 'Work Projects', color: 'bg-indigo-500', count: 24 },
        { label: 'Personal', color: 'bg-emerald-500', count: 12 },
        { label: 'Archives', color: 'bg-amber-500', count: 8 },
    ];
</script>

<aside class="w-80 bg-white dark:bg-slate-900 h-screen flex flex-col border-r border-slate-200/50 dark:border-slate-800/50 z-30 transition-colors duration-300">
    <!-- Action Button -->
    <div class="p-8">
        <button 
            onclick={() => document.getElementById('create-btn')?.click()}
            class="w-full flex items-center justify-center space-x-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-[24px] py-4 shadow-xl shadow-indigo-200 dark:shadow-indigo-950/20 transition-all active:scale-95 group"
        >
            <div class="bg-white/20 p-1.5 rounded-xl group-hover:rotate-90 transition-transform duration-500">
                <Plus class="w-5 h-5 stroke-[3px]" />
            </div>
            <span class="font-bold text-lg tracking-tight">New Asset</span>
        </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 space-y-8 overflow-y-auto custom-scrollbar">
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
                <button class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
                    <Plus class="w-3 h-3 text-slate-400" />
                </button>
            </div>
            <div class="space-y-1">
                {#each categories as cat}
                    <button class="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-2xl transition-all group text-left">
                        <div class="flex items-center space-x-3">
                            <div class={cn("w-2 h-2 rounded-full shadow-sm", cat.color)}></div>
                            <span class="font-bold text-sm text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-slate-100">{cat.label}</span>
                        </div>
                        <span class="text-[10px] font-black text-slate-300 dark:text-slate-600 group-hover:text-slate-400">{cat.count}</span>
                    </button>
                {/each}
            </div>
        </div>

        <!-- Tools Section -->
        <div>
            <div class="px-4 mb-4">
                <span class="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Tools</span>
            </div>
            <div class="space-y-1 text-slate-600 dark:text-slate-400">
                <button class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-2xl transition-all group">
                    <Zap class="w-5 h-5 text-slate-400 dark:text-slate-500 group-hover:text-amber-500 transition-colors" />
                    <span class="font-bold text-sm tracking-tight">Quick Actions</span>
                </button>
                <button class="w-full flex items-center space-x-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-2xl transition-all group">
                    <ShieldCheck class="w-5 h-5 text-slate-400 dark:text-slate-500 group-hover:text-emerald-500 transition-colors" />
                    <span class="font-bold text-sm tracking-tight">Privacy Scan</span>
                </button>
            </div>
        </div>
    </nav>

    <!-- Storage Widget -->
    <div class="p-6">
        <div class="bg-slate-50 dark:bg-slate-800/50 rounded-[32px] p-6 border border-slate-100 dark:border-slate-800 relative overflow-hidden group">
            <div class="relative z-10">
                <div class="flex items-center justify-between mb-4">
                    <div class="bg-white dark:bg-slate-700 p-2 rounded-xl shadow-sm">
                        <Database class="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <button class="text-[10px] font-black text-white bg-indigo-600 px-3 py-1.5 rounded-full hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-100 dark:shadow-none">UPGRADE</button>
                </div>
                <div class="space-y-2">
                    <div class="flex justify-between items-end">
                        <p class="text-xs font-black text-slate-700 dark:text-slate-200">Cloud Storage</p>
                        <p class="text-[10px] font-bold text-slate-400">45% used</p>
                    </div>
                    <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                        <div class="bg-gradient-to-r from-indigo-500 via-indigo-600 to-violet-600 h-full rounded-full transition-all duration-1000" style="width: 45%"></div>
                    </div>
                    <p class="text-[10px] font-bold text-slate-400 leading-relaxed">
                        <span class="text-slate-700 dark:text-slate-200">6.8 GB</span> of 15 GB total
                    </p>
                </div>
            </div>
            <!-- Decorative circle -->
            <div class="absolute -bottom-8 -right-8 w-24 h-24 bg-indigo-500/5 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
        </div>
    </div>
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
