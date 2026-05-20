<script lang="ts">
    import { X, Download, ExternalLink, Maximize2, Minimize2, File as FileIcon, Image as ImageIcon, Music, Video, FileText, FileCode } from 'lucide-svelte';
    import api, { BASE_URL } from '$lib/api';
    import { onMount } from 'svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { cn } from '$lib/utils';

    let { item, onclose, ondownload } = $props<{
        item: any;
        onclose: () => void;
        ondownload: () => void;
    }>();

    let isFullScreen = $state(false);
    let blobUrl = $state<string | null>(null);
    let loading = $state(true);

    async function loadFile() {
        loading = true;
        try {
            const response = await api.get(`/items/${item.id}/download`, {
                responseType: 'blob'
            });
            blobUrl = window.URL.createObjectURL(new Blob([response.data], { type: item.mime_type }));
        } catch (e) {
            console.error('Preview error:', e);
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        loadFile();
        return () => {
            if (blobUrl) window.URL.revokeObjectURL(blobUrl);
        };
    });

    function getFileType(mime: string = '') {
        const m = mime.toLowerCase();
        if (m.includes('image')) return 'image';
        if (m.includes('video')) return 'video';
        if (m.includes('pdf')) return 'pdf';
        if (m.includes('text') || m.includes('javascript') || m.includes('json') || m.includes('html') || m.includes('css')) return 'text';
        return 'other';
    }

    const type = getFileType(item.mime_type);
</script>

<div 
    class="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-12"
    transition:fade={{ duration: 200 }}
>
    <!-- Backdrop -->
    <div 
        class="absolute inset-0 bg-slate-900/90 dark:bg-[#020617]/95 backdrop-blur-xl"
        onclick={onclose}
    ></div>

    <!-- Preview Container -->
    <div 
        class={cn(
            "bg-white dark:bg-slate-900 rounded-[40px] shadow-2xl border border-white/20 dark:border-slate-800 relative overflow-hidden flex flex-col transition-all duration-500 ease-out",
            isFullScreen ? "w-full h-full rounded-none" : "w-full max-w-5xl h-[85vh]"
        )}
        transition:scale={{ duration: 400, start: 0.95, easing: quintOut }}
        onclick={(e) => e.stopPropagation()}
    >
        <!-- Toolbar -->
        <div class="flex items-center justify-between px-8 py-6 border-b border-slate-100 dark:border-slate-800 shrink-0">
            <div class="flex items-center space-x-4 min-w-0">
                <div class="bg-indigo-600/10 p-2.5 rounded-2xl shrink-0">
                    <FileIcon class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div class="min-w-0">
                    <h3 class="font-black text-slate-900 dark:text-white truncate tracking-tight">{item.name}</h3>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest truncate">{item.mime_type || 'Unclassified'}</p>
                </div>
            </div>

            <div class="flex items-center space-x-2">
                <button 
                    onclick={ondownload}
                    class="p-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-2xl text-slate-400 hover:text-indigo-600 transition-all active:scale-90"
                    title="Download"
                >
                    <Download class="w-5 h-5" />
                </button>
                <button 
                    onclick={() => isFullScreen = !isFullScreen}
                    class="p-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-2xl text-slate-400 hover:text-indigo-600 transition-all active:scale-90"
                    title={isFullScreen ? "Exit Fullscreen" : "Fullscreen"}
                >
                    {#if isFullScreen}
                        <Minimize2 class="w-5 h-5" />
                    {:else}
                        <Maximize2 class="w-5 h-5" />
                    {/if}
                </button>
                <div class="w-px h-6 bg-slate-100 dark:bg-slate-800 mx-2"></div>
                <button 
                    onclick={onclose}
                    class="p-3 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-2xl text-slate-400 hover:text-rose-600 transition-all active:scale-90"
                >
                    <X class="w-6 h-6" />
                </button>
            </div>
        </div>

        <!-- Content Area -->
        <div class="flex-1 overflow-hidden bg-slate-50 dark:bg-[#020617]/50 relative flex items-center justify-center">
            {#if loading}
                <div class="flex flex-col items-center space-y-4" in:fade>
                    <div class="w-12 h-12 border-4 border-indigo-600/20 border-t-indigo-600 rounded-full animate-spin"></div>
                    <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] animate-pulse">Decrypting File...</p>
                </div>
            {:else if blobUrl}
                {#if type === 'image'}
                    <img 
                        src={blobUrl} 
                        alt={item.name} 
                        class="max-w-full max-h-full object-contain shadow-2xl"
                        in:fade={{ duration: 400 }}
                    />
                {:else if type === 'pdf'}
                    <iframe 
                        src={blobUrl} 
                        title={item.name}
                        class="w-full h-full border-none"
                    ></iframe>
                {:else if type === 'video'}
                    <video 
                        controls 
                        autoplay
                        class="max-w-full max-h-full shadow-2xl"
                    >
                        <source src={blobUrl} type={item.mime_type}>
                        Your browser does not support the video tag.
                    </video>
                {:else if type === 'text'}
                    <iframe 
                        src={blobUrl} 
                        title={item.name}
                        class="w-full h-full border-none bg-white"
                    ></iframe>
                {/if}
            {:else}
                <div class="text-center" in:fade>
                    <div class="bg-indigo-600/5 w-24 h-24 rounded-[32px] flex items-center justify-center mx-auto mb-6">
                        <FileIcon class="w-12 h-12 text-indigo-200" />
                    </div>
                    <h4 class="text-xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">Preview Unavailable</h4>
                    <p class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-8 max-w-xs mx-auto">This file type cannot be previewed directly in the browser.</p>
                    <button 
                        onclick={ondownload}
                        class="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-[24px] shadow-xl shadow-indigo-500/20 transition-all active:scale-95 flex items-center space-x-3 mx-auto"
                    >
                        <Download class="w-5 h-5" />
                        <span>Download to View</span>
                    </button>
                </div>
            {/if}
        </div>

        <!-- Footer Info -->
        <div class="px-8 py-4 bg-white dark:bg-slate-900 border-t border-slate-50 dark:border-slate-800 flex items-center justify-between shrink-0">
            <span class="text-[10px] font-black text-slate-300 dark:text-slate-700 uppercase tracking-[0.4em]">DRIVE X SECURE PREVIEW NODE</span>
            <div class="flex items-center space-x-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                <span>ID: {item.id.split('-')[0]}</span>
                <span class="w-1 h-1 bg-slate-200 rounded-full"></span>
                <span>Type: {type}</span>
            </div>
        </div>
    </div>
</div>
