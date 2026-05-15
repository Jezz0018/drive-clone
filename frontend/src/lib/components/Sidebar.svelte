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
        ShieldCheck
    } from 'lucide-svelte';
    import { page } from '$app/stores';
    import { cn } from '$lib/utils';

    let { activeView = 'my-drive' } = $props();

    const menuItems = [
        { id: 'my-drive', label: 'All Files', icon: HardDrive, path: '/' },
        { id: 'recent', label: 'Recent', icon: Clock, path: '/recent' },
        { id: 'starred', label: 'Favorites', icon: Star, path: '/starred' },
        { id: 'shared', label: 'Shared', icon: Share2, path: '/shared' },
        { id: 'trash', label: 'Trash', icon: Trash2, path: '/trash' },
    ];

    const tags = [
        { label: 'Personal', color: 'bg-indigo-400' },
        { label: 'Work', color: 'bg-emerald-400' },
        { label: 'Finance', color: 'bg-amber-400' },
    ];
</script>

<aside class="w-72 bg-white h-screen flex flex-col border-r border-slate-100 z-30">
    <div class="p-6">
        <button class="w-full flex items-center justify-center space-x-3 bg-indigo-600 text-white rounded-2xl px-4 py-4 shadow-lg shadow-indigo-100 hover:shadow-indigo-200 hover:bg-indigo-700 transition-all group">
            <div class="bg-white/20 p-1 rounded-lg group-hover:rotate-90 transition-transform duration-300">
                <Plus class="w-5 h-5" />
            </div>
            <span class="font-bold tracking-wide">Upload New</span>
        </button>
    </div>

    <nav class="flex-1 px-4 space-y-1.5 overflow-y-auto">
        <div class="px-3 mb-2">
            <span class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Main Menu</span>
        </div>
        {#each menuItems as item}
            {@const Icon = item.icon}
            <a 
                href={item.path}
                class={cn(
                    "flex items-center justify-between px-4 py-3 rounded-xl transition-all group",
                    activeView === item.id 
                        ? "bg-indigo-50 text-indigo-600 shadow-sm shadow-indigo-50/50" 
                        : "hover:bg-slate-50 text-slate-600 hover:text-slate-900"
                )}
            >
                <div class="flex items-center space-x-3">
                    <Icon class={cn("w-5 h-5 transition-colors", activeView === item.id ? "text-indigo-600" : "text-slate-400 group-hover:text-slate-600")} />
                    <span class="font-semibold text-sm">{item.label}</span>
                </div>
                {#if item.id === 'trash'}
                    <span class="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-bold">12</span>
                {/if}
            </a>
        {/each}

        <div class="px-3 mt-8 mb-2">
            <span class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Categories</span>
        </div>
        {#each tags as tag}
            <button class="w-full flex items-center space-x-3 px-4 py-2.5 hover:bg-slate-50 rounded-xl transition-all group">
                <div class={cn("w-2 h-2 rounded-full", tag.color)}></div>
                <span class="text-sm font-semibold text-slate-600 group-hover:text-slate-900">{tag.label}</span>
            </button>
        {/each}
    </nav>

    <div class="p-6 mt-auto">
        <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center space-x-2">
                    <Database class="w-4 h-4 text-indigo-500" />
                    <span class="text-xs font-bold text-slate-700">Storage</span>
                </div>
                <span class="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">Upgrade</span>
            </div>
            <div class="w-full bg-slate-200 rounded-full h-2 mb-2 overflow-hidden">
                <div class="bg-gradient-to-r from-indigo-500 to-violet-500 h-full rounded-full" style="width: 45%"></div>
            </div>
            <div class="flex justify-between items-center">
                <span class="text-[10px] font-medium text-slate-500">6.8 GB of 15 GB</span>
                <span class="text-[10px] font-bold text-slate-700 text-right">45%</span>
            </div>
        </div>

        <button class="w-full mt-4 flex items-center justify-center space-x-2 text-slate-400 hover:text-indigo-600 transition-colors py-2 group">
            <ShieldCheck class="w-4 h-4" />
            <span class="text-[10px] font-bold uppercase tracking-wider">Security Verified</span>
        </button>
    </div>
</aside>

