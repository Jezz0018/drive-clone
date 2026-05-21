<script lang="ts">
    import Header from '$lib/components/Header.svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import api from '$lib/api';
    import { onMount } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import { 
        Activity as ActivityIcon, 
        Upload, 
        FolderPlus, 
        Trash2, 
        Edit3, 
        Star, 
        Archive,
        Clock,
        FileText,
        ChevronRight
    } from 'lucide-svelte';
    import { cn } from '$lib/utils';

    let activities = $state<any[]>([]);
    let loading = $state(true);

    async function fetchActivities() {
        try {
            const response = await api.get('/items/activity', { params: { limit: 50 } });
            activities = response.data;
        } catch (e) {}
        finally {
            loading = false;
        }
    }

    onMount(fetchActivities);

    function getActionIcon(action: string) {
        switch(action) {
            case 'upload': return Upload;
            case 'create_folder': return FolderPlus;
            case 'delete': return Trash2;
            case 'update': return Edit3;
            case 'star': return Star;
            case 'archive': return Archive;
            default: return ActivityIcon;
        }
    }

    function getActionColor(action: string) {
        switch(action) {
            case 'upload': return 'text-indigo-600 bg-indigo-100 dark:text-indigo-400 dark:bg-indigo-900/30';
            case 'create_folder': return 'text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30';
            case 'delete': return 'text-rose-600 bg-rose-100 dark:text-rose-400 dark:bg-rose-900/30';
            case 'update': return 'text-emerald-600 bg-emerald-100 dark:text-emerald-400 dark:bg-emerald-900/30';
            default: return 'text-slate-600 bg-slate-100 dark:text-slate-400 dark:bg-slate-900/30';
        }
    }

    function formatAction(action: string) {
        return action.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
</script>

<div class="h-screen flex flex-col">
    <Header />
    <div class="flex-1 flex overflow-hidden">
        <Sidebar activeView="activities" />
        
        <div class="flex-1 flex flex-col bg-slate-100 dark:bg-[#0f172a] monochrome:bg-black overflow-hidden transition-colors duration-300">
            <div class="px-8 pt-8 -mb-4">
                <h1 class="text-4xl font-black text-slate-900 dark:text-white monochrome:text-white tracking-tighter flex items-center space-x-3">
                    <span>Activities</span>
                    <ActivityIcon class="w-8 h-8 text-indigo-500" />
                </h1>
            </div>

            <div class="flex items-center space-x-1 px-8 py-8 overflow-x-auto no-scrollbar">
                <div class="flex items-center px-3 py-1.5 rounded-xl font-bold text-sm bg-indigo-50 dark:bg-indigo-900/20 monochrome:bg-white/10 text-indigo-600 dark:text-indigo-400 monochrome:text-white">
                    Timeline
                </div>
            </div>

            <main class="flex-1 overflow-y-auto px-8 pb-12 custom-scrollbar">
                {#if loading}
                    <div class="space-y-4">
                        {#each Array(8) as _}
                            <div class="h-24 bg-white/50 dark:bg-slate-800/30 monochrome:bg-white/5 rounded-[32px] animate-pulse"></div>
                        {/each}
                    </div>
                {:else if activities.length === 0}
                    <div class="flex flex-col items-center justify-center h-[50vh] text-center" in:fade>
                        <div class="bg-indigo-600/5 w-32 h-32 rounded-[40px] flex items-center justify-center mb-8">
                            <ActivityIcon class="w-16 h-16 text-indigo-200 dark:text-indigo-900/40" />
                        </div>
                        <h3 class="text-3xl font-black text-slate-900 dark:text-white tracking-tighter mb-3">No Activity Yet</h3>
                        <p class="text-slate-400 font-bold uppercase tracking-widest text-xs">Start using your drive to see events here</p>
                    </div>
                {:else}
                    <div class="space-y-2" in:fly={{ y: 20, duration: 400 }}>
                        {#each activities as act (act.id)}
                            {@const Icon = getActionIcon(act.action)}
                            <div class="group bg-white dark:bg-slate-800/40 monochrome:bg-black px-8 py-5 rounded-[24px] border border-slate-200 dark:border-slate-800 monochrome:border-white/10 hover:border-indigo-500/50 dark:hover:border-indigo-400/50 transition-all duration-300 flex items-center">
                                <!-- Name (Left) -->
                                <div class="flex-1 min-w-0 flex items-center space-x-4">
                                    <div class={cn("w-10 h-10 rounded-xl flex items-center justify-center shrink-0", getActionColor(act.action))}>
                                        <Icon class="w-5 h-5" />
                                    </div>
                                    <h4 class="text-lg font-bold text-slate-900 dark:text-white monochrome:text-white truncate tracking-tight">
                                        {act.item_name}
                                    </h4>
                                </div>

                                <!-- Action (Center-ish) -->
                                <div class="w-48 hidden md:block">
                                    <span class={cn(
                                        "px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest",
                                        act.action === 'upload' ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" :
                                        act.action === 'delete' ? "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400" :
                                        act.action === 'update' ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" :
                                        act.action === 'create_folder' ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400" :
                                        "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400"
                                    )}>
                                        {formatAction(act.action)}
                                    </span>
                                </div>

                                <!-- Time (Right) -->
                                <div class="w-64 text-right hidden sm:block">
                                    <div class="flex items-center justify-end text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                                        <Clock class="w-3.5 h-3.5 mr-2 opacity-50" />
                                        {new Date(act.created_at).toLocaleDateString()}
                                        <span class="mx-2 opacity-30">|</span>
                                        {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </main>
        </div>
    </div>
</div>

<style>
    @reference "../../routes/layout.css";
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    .custom-scrollbar::-webkit-scrollbar { width: 4px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
    .custom-scrollbar::-webkit-scrollbar-thumb { @apply bg-slate-200 dark:bg-slate-800 monochrome:bg-white/20 rounded-full; }
</style>
