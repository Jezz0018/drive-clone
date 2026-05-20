<script lang="ts">
    import { page } from '$app/state';
    import { onMount } from 'svelte';
    import api, { BASE_URL } from '$lib/api';
    import { 
        File as FileIcon, 
        Download, 
        Shield, 
        Globe, 
        Clock, 
        HardDrive,
        Image as ImageIcon,
        Music,
        Video,
        FileText,
        FileCode,
        Archive as ArchiveIcon,
        ArrowRight
    } from 'lucide-svelte';
    import { cn } from '$lib/utils';
    import { fade, fly, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    const token = page.params.token;
    let item = $state<any>(null);
    let loading = $state(true);
    let error = $state<string | null>(null);

    async function fetchSharedItem() {
        loading = true;
        try {
            const response = await api.get(`/items/share/${token}/info`);
            item = response.data;
        } catch (e: any) {
            error = e.response?.data?.detail || "Shared link is invalid or has expired.";
        } finally {
            loading = false;
        }
    }

    function getFileIcon(item: any) {
        if (!item) return FileIcon;
        const mime = item.mime_type?.toLowerCase() || '';
        if (mime.includes('image')) return ImageIcon;
        if (mime.includes('video')) return Video;
        if (mime.includes('audio')) return Music;
        if (mime.includes('text') || mime.includes('pdf')) return FileText;
        if (mime.includes('javascript') || mime.includes('json') || mime.includes('html')) return FileCode;
        if (mime.includes('zip') || mime.includes('rar') || mime.includes('tar')) return ArchiveIcon;
        return FileIcon;
    }

    function formatSize(bytes?: number) {
        if (!bytes) return '-';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function downloadFile() {
        window.open(`${BASE_URL}/items/share/${token}`, '_blank');
    }

    onMount(fetchSharedItem);
</script>

<div class="min-h-screen bg-slate-50 dark:bg-[#020617] flex flex-col items-center justify-center p-6 selection:bg-indigo-100 selection:text-indigo-900">
    <!-- Background Accents -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
        <div class="absolute -top-[20%] -right-[10%] w-[60%] h-[60%] bg-indigo-500/5 dark:bg-indigo-500/10 blur-[120px] rounded-full"></div>
        <div class="absolute -bottom-[20%] -left-[10%] w-[60%] h-[60%] bg-blue-500/5 dark:bg-blue-500/10 blur-[120px] rounded-full"></div>
    </div>

    {#if loading}
        <div class="flex flex-col items-center space-y-6" in:fade>
            <div class="relative">
                <div class="w-24 h-24 border-4 border-slate-200 dark:border-slate-800 rounded-[32px] animate-pulse"></div>
                <div class="absolute inset-0 border-t-4 border-indigo-600 rounded-[32px] animate-spin"></div>
            </div>
            <p class="text-sm font-black text-slate-400 uppercase tracking-[0.3em] animate-pulse">Establishing Secure Link...</p>
        </div>
    {:else if error}
        <div class="w-full max-w-md bg-white dark:bg-slate-900 rounded-[48px] p-12 text-center shadow-2xl border border-slate-100 dark:border-slate-800 relative overflow-hidden" in:fly={{ y: 20, duration: 600 }}>
            <div class="bg-rose-50 dark:bg-rose-900/20 w-20 h-20 rounded-[32px] flex items-center justify-center mx-auto mb-8">
                <Shield class="w-10 h-10 text-rose-600 dark:text-rose-400" />
            </div>
            <h1 class="text-2xl font-black text-slate-900 dark:text-white tracking-tight mb-4">Access Denied</h1>
            <p class="text-slate-500 dark:text-slate-400 font-medium leading-relaxed mb-10">{error}</p>
            <a href="/" class="inline-flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 font-black uppercase tracking-widest text-xs hover:underline">
                <span>Go to Drive Home</span>
                <ArrowRight class="w-4 h-4" />
            </a>
        </div>
    {:else if item}
        {@const Icon = getFileIcon(item)}
        <div class="w-full max-w-2xl" in:fly={{ y: 30, duration: 800, easing: quintOut }}>
            <div class="bg-white dark:bg-slate-900 rounded-[56px] p-12 shadow-2xl border border-white/20 dark:border-slate-800 relative overflow-hidden group">
                <!-- Share Badge -->
                <div class="absolute top-8 right-8 flex items-center space-x-2 bg-emerald-50 dark:bg-emerald-900/20 px-4 py-2 rounded-full border border-emerald-100/50 dark:border-emerald-800/50">
                    <Globe class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                    <span class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">Public Link</span>
                </div>

                <div class="flex flex-col items-center text-center">
                    <!-- File Icon -->
                    <div class="relative mb-10">
                        <div class="w-32 h-32 bg-indigo-50 dark:bg-indigo-900/20 rounded-[44px] flex items-center justify-center transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3 shadow-xl shadow-indigo-500/5">
                            <svelte:component this={Icon} class="w-16 h-16 text-indigo-600 dark:text-indigo-400 stroke-[1.5px]" />
                        </div>
                        <div class="absolute -bottom-2 -right-2 bg-white dark:bg-slate-800 p-3 rounded-2xl shadow-xl border border-slate-50 dark:border-slate-700">
                            <Download class="w-5 h-5 text-indigo-600" />
                        </div>
                    </div>

                    <!-- Details -->
                    <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tighter mb-4 max-w-lg break-words">{item.name}</h1>
                    
                    <div class="flex items-center justify-center space-x-6 mb-12">
                        <div class="flex items-center space-x-2">
                            <HardDrive class="w-4 h-4 text-slate-400" />
                            <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">{formatSize(item.size)}</span>
                        </div>
                        <div class="w-1 h-1 bg-slate-200 dark:bg-slate-800 rounded-full"></div>
                        <div class="flex items-center space-x-2">
                            <Clock class="w-4 h-4 text-slate-400" />
                            <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">{new Date(item.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                        </div>
                    </div>

                    <!-- Action -->
                    <button 
                        onclick={downloadFile}
                        class="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-6 rounded-[32px] text-lg font-black shadow-2xl shadow-indigo-500/20 dark:shadow-none transition-all active:scale-[0.98] flex items-center justify-center space-x-4 group/btn"
                    >
                        <span>DOWNLOAD FILE</span>
                        <Download class="w-6 h-6 transition-transform group-hover/btn:-translate-y-1" />
                    </button>

                    <p class="mt-8 text-[10px] font-black text-slate-300 dark:text-slate-700 uppercase tracking-[0.4em]">
                        SECURE TRANSFER NODE - ENCRYPTED AT REST
                    </p>
                </div>
            </div>

            <!-- Promotion Footer -->
            <div class="mt-12 text-center">
                <p class="text-slate-400 dark:text-slate-500 text-sm font-medium mb-4">Powered by</p>
                <div class="flex items-center justify-center space-x-2">
                    <div class="bg-indigo-600 p-2 rounded-xl">
                        <HardDrive class="w-5 h-5 text-white" />
                    </div>
                    <span class="text-xl font-black text-slate-900 dark:text-white tracking-tighter">DRIVE X</span>
                </div>
                <div class="mt-8">
                    <a href="/signup" class="px-6 py-3 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-black uppercase tracking-widest rounded-2xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 transition-all">
                        Create Your Own Cloud
                    </a>
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
    :global(body) {
        @apply transition-colors duration-300;
    }
</style>
