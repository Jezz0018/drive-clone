<script lang="ts">
    import Header from '$lib/components/Header.svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import { Database, HardDrive, PieChart, Layers, RefreshCw } from 'lucide-svelte';
    import { fly, fade } from 'svelte/transition';
    import { toasts } from '$lib/toasts';
    import { onMount } from 'svelte';
    import api from '$lib/api';

    let usageData = $state<{used: number, limit: number, breakdown: any[]}>({
        used: 0,
        limit: 10 * 1024 * 1024 * 1024,
        breakdown: []
    });
    let loading = $state(true);

    async function fetchUsage() {
        try {
            const response = await api.get(`/items/storage/usage?t=${Date.now()}`);
            console.log('Storage usage response:', response.data);
            usageData = response.data;
        } catch (e) {
            toasts.error('Failed to sync storage data');
        } finally {
            loading = false;
        }
    }

    onMount(fetchUsage);

    function formatSize(bytes?: number) {
        if (bytes === 0) return '0 Bytes';
        if (!bytes) return 'Syncing...';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        // Use higher precision for MB if the user expects to see small changes
        const precision = i === 2 ? 2 : 1; 
        return parseFloat((bytes / Math.pow(k, i)).toFixed(precision)) + ' ' + sizes[i];
    }

    const categoryColors: Record<string, string> = {
        'Work': 'bg-indigo-500',
        'Personal': 'bg-emerald-500',
        'Uncategorized': 'bg-slate-400',
        'Shared': 'bg-rose-500'
    };

    function getColor(name: string) {
        return categoryColors[name] || 'bg-violet-500';
    }

    // Use 2 decimal places for internal percentage calculation to ensure gauge movement
    let rawPercentage = $derived((usageData.used / usageData.limit) * 100);
    let displayPercentage = $derived(rawPercentage < 0.1 && usageData.used > 0 ? '< 0.1' : Math.round(rawPercentage));
</script>

<svelte:head>
    <title>Storage Settings | DRIVE X</title>
</svelte:head>

<div class="h-screen flex flex-col">
    <Header />
    <div class="flex-1 flex overflow-hidden">
        <Sidebar activeView="storage" />
        
        <main class="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#0f172a] p-8 custom-scrollbar">
            <div class="max-w-4xl mx-auto space-y-8" in:fly={{ y: 20, duration: 600 }}>
                    <div class="flex items-center justify-between mb-8">
                        <div class="flex flex-col">
                            <div class="flex items-center space-x-2 text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-1">
                                <Database class="w-3 h-3" />
                                <span>Infrastructure Control</span>
                            </div>
                            <h1 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">Storage Settings</h1>
                        </div>
                        <button 
                            onclick={async () => {
                                await fetchUsage();
                                alert(`Storage API raw: used=${usageData.used} bytes, files=${usageData.file_count}`);
                            }}
                            class="p-3 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-2xl text-indigo-600 transition-all active:scale-90"
                            title="Diagnostics"
                        >
                            <RefreshCw class="w-5 h-5" />
                        </button>
                    </div>

                <div class="bg-white dark:bg-slate-900 rounded-[40px] border border-slate-200/50 dark:border-slate-800 shadow-sm overflow-hidden p-10">
                    <div class="space-y-12">
                        <!-- Graphical Summary -->
                        <div class="flex flex-col lg:flex-row gap-12 items-center">
                            <!-- Donut Gauge -->
                            <div class="relative w-56 h-56 flex items-center justify-center">
                                <svg class="w-full h-full -rotate-90">
                                    <circle
                                        cx="112" cy="112" r="90"
                                        fill="transparent"
                                        stroke="currentColor"
                                        stroke-width="20"
                                        class="text-slate-100 dark:text-slate-800"
                                    />
                                    <circle
                                        cx="112" cy="112" r="90"
                                        fill="transparent"
                                        stroke="currentColor"
                                        stroke-width="20"
                                        stroke-dasharray={2 * Math.PI * 90}
                                        stroke-dashoffset={2 * Math.PI * 90 * (1 - rawPercentage / 100)}
                                        stroke-linecap="round"
                                        class="text-indigo-600 transition-all duration-1000 ease-out"
                                    />
                                </svg>
                                <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                                    <span class="text-4xl font-black text-slate-900 dark:text-white">{displayPercentage}%</span>
                                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Utilized</span>
                                </div>
                            </div>

                            <div class="flex-1 space-y-6 w-full">
                                <div>
                                    <h2 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Resource Allocation</h2>
                                    <p class="text-sm text-slate-500 dark:text-slate-400 font-medium mt-1">Real-time breakdown across your secure drive</p>
                                </div>

                                <div class="space-y-4">
                                    <div class="flex justify-between items-end">
                                        <div class="flex items-center space-x-2">
                                            <HardDrive class="w-4 h-4 text-indigo-600" />
                                            <span class="text-sm font-bold text-slate-700 dark:text-slate-200">{formatSize(usageData.used)} of {formatSize(usageData.limit)}</span>
                                        </div>
                                        <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">{formatSize(usageData.limit - usageData.used)} Available</span>
                                    </div>

                                    <!-- Stacked Progress Bar -->
                                    <div class="h-4 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex shadow-inner">
                                        {#each usageData.breakdown as cat}
                                            <div 
                                                class={cn("h-full transition-all duration-1000", getColor(cat.name))}
                                                style="width: {(cat.size / usageData.limit) * 100}%"
                                                title="{cat.name}: {formatSize(cat.size)}"
                                            ></div>
                                        {/each}
                                    </div>

                                    <!-- Legend -->
                                    <div class="flex flex-wrap gap-4 pt-2">
                                        {#each usageData.breakdown as cat}
                                            <div class="flex items-center space-x-2">
                                                <div class={cn("w-2.5 h-2.5 rounded-full", getColor(cat.name))}></div>
                                                <span class="text-xs font-bold text-slate-600 dark:text-slate-400">{cat.name}</span>
                                                <span class="text-[10px] text-slate-400 font-medium">({Math.round((cat.size / usageData.used) * 100) || 0}%)</span>
                                            </div>
                                        {/each}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- System Capabilities -->
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-slate-100 dark:border-slate-800">
                            <div class="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-[32px] border border-slate-100 dark:border-slate-800 group hover:border-indigo-500/30 transition-all">
                                <div class="p-3 rounded-2xl bg-white dark:bg-slate-700 w-fit mb-4 shadow-sm group-hover:scale-110 transition-transform">
                                    <PieChart class="w-5 h-5 text-indigo-600" />
                                </div>
                                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Mirror Nodes</p>
                                <p class="text-2xl font-black text-slate-900 dark:text-white">3 Active</p>
                            </div>
                            <div class="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-[32px] border border-slate-100 dark:border-slate-800 group hover:border-indigo-500/30 transition-all">
                                <div class="p-3 rounded-2xl bg-white dark:bg-slate-700 w-fit mb-4 shadow-sm group-hover:scale-110 transition-transform">
                                    <Layers class="w-5 h-5 text-emerald-600" />
                                </div>
                                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Encryption</p>
                                <p class="text-2xl font-black text-slate-900 dark:text-white">AES-256</p>
                            </div>
                            <div class="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-[32px] border border-slate-100 dark:border-slate-800 group hover:border-indigo-500/30 transition-all">
                                <div class="p-3 rounded-2xl bg-white dark:bg-slate-700 w-fit mb-4 shadow-sm group-hover:scale-110 transition-transform">
                                    <Database class="w-5 h-5 text-amber-600" />
                                </div>
                                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Syncing</p>
                                <p class="text-2xl font-black text-slate-900 dark:text-white">Live-Stream</p>
                            </div>
                        </div>

                        <!-- Upgrade CTA -->
                        <div class="p-10 rounded-[40px] bg-linear-to-br from-indigo-600 to-violet-700 text-white shadow-2xl shadow-indigo-500/30">
                            <div class="flex flex-col md:flex-row md:items-center justify-between gap-10">
                                <div class="flex-1 space-y-4">
                                    <h3 class="text-3xl font-black tracking-tight leading-none">Expand your universe.</h3>
                                    <p class="text-indigo-100 font-medium leading-relaxed max-w-lg">Upgrade to a Enterprise identity to increase your storage capacity up to 2 TB, enable real-time collaboration, and unlock advanced version control.</p>
                                </div>
                                <button 
                                    onclick={() => toasts.info('Upgrade plans coming soon!')}
                                    class="px-10 py-5 bg-white text-indigo-600 font-black rounded-3xl hover:bg-indigo-50 transition-all active:scale-95 shadow-xl whitespace-nowrap"
                                >
                                    Get More Space
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</div>

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
