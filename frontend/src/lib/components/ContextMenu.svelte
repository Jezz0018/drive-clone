<script lang="ts">
    import { 
        Star, 
        Archive, 
        Share2, 
        Download, 
        Trash2, 
        Tag, 
        MoreVertical,
        ChevronRight,
        RefreshCcw,
        Folder,
        Info,
        Pin,
        PinOff,
        Move
    } from 'lucide-svelte';
    import { fade, scale, slide } from 'svelte/transition';
    import { cn } from '$lib/utils';

    let { 
        x, 
        y, 
        item, 
        categories = [], 
        onclose,
        onaction
    } = $props<{
        x: number;
        y: number;
        item: any;
        categories: any[];
        onclose: () => void;
        onaction: (action: string, data?: any) => void;
    }>();

    let showCategories = $state(false);

    function handleAction(action: string, data?: any) {
        onaction(action, data);
        onclose();
    }

    // Close on click outside
    function handleWindowClick() {
        onclose();
    }
</script>

<svelte:window onclick={handleWindowClick} oncontextmenu={handleWindowClick} />

<div 
    class="fixed z-[100] min-w-[220px] bg-white dark:bg-slate-900 monochrome:bg-black border border-slate-200 dark:border-slate-800 monochrome:border-white/20 rounded-2xl shadow-2xl p-2 py-3 overflow-hidden"
    style="left: {x}px; top: {y}px;"
    transition:scale={{ duration: 150, start: 0.95 }}
    onclick={(e) => e.stopPropagation()}
>
    <div class="space-y-0.5">
        {#if item.is_trashed}
            <button 
                onclick={() => handleAction('restore')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-emerald-50 dark:hover:bg-emerald-900/20 monochrome:hover:bg-white/10 text-emerald-600 dark:text-emerald-400 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <RefreshCcw class="w-4 h-4 icon-bounce" />
                    <span class="text-sm font-bold">Restore File</span>
                </div>
            </button>

            <button 
                onclick={() => handleAction('trash')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-rose-50 dark:hover:bg-rose-900/20 monochrome:hover:bg-white/10 text-rose-600 dark:text-rose-400 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <Trash2 class="w-4 h-4 icon-bounce" />
                    <span class="text-sm font-bold">Delete Permanently</span>
                </div>
            </button>
        {:else}
            <button 
                onclick={() => handleAction('details')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <Info class="w-4 h-4 text-slate-400 group-hover:text-indigo-600 monochrome:text-white/60 monochrome:group-hover:text-white transition-colors icon-bounce" />
                    <span class="text-sm font-bold">View Details</span>
                </div>
            </button>

            <button 
                onclick={() => handleAction('pin')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <svelte:component this={item.is_pinned ? PinOff : Pin} class={cn("w-4 h-4 transition-colors icon-bounce", item.is_pinned ? "text-indigo-600 monochrome:text-white" : "text-slate-400 group-hover:text-indigo-600 monochrome:text-white/60 monochrome:group-hover:text-white")} />
                    <span class="text-sm font-bold">{item.is_pinned ? 'Unpin from Sidebar' : 'Pin to Sidebar'}</span>
                </div>
            </button>

            <button 
                onclick={() => handleAction('star')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <Star class={cn("w-4 h-4 transition-colors icon-bounce", item.is_starred ? "text-amber-500 fill-current monochrome:text-white" : "text-slate-400 group-hover:text-indigo-600 monochrome:text-white/60 monochrome:group-hover:text-white")} />
                    <span class="text-sm font-bold">{item.is_starred ? 'Remove Favorite' : 'Mark Favorite'}</span>
                </div>
            </button>

            <button 
                onclick={() => handleAction('archive')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <Archive class={cn("w-4 h-4 transition-colors icon-bounce", item.is_archived ? "text-indigo-600 monochrome:text-white" : "text-slate-400 group-hover:text-indigo-600 monochrome:text-white/60 monochrome:group-hover:text-white")} />
                    <span class="text-sm font-bold">{item.is_archived ? 'Unarchive' : 'Archive'}</span>
                </div>
            </button>

            <button 
                onclick={() => handleAction('share')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <Share2 class="w-4 h-4 text-slate-400 group-hover:text-indigo-600 monochrome:text-white/60 monochrome:group-hover:text-white transition-colors icon-bounce" />
                    <span class="text-sm font-bold">Share Link</span>
                </div>
            </button>

            <button 
                onclick={() => handleAction('move')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <div class="bg-indigo-100 dark:bg-indigo-900/30 monochrome:bg-white/10 p-1.5 rounded-lg group-hover:scale-110 transition-transform">
                        <Folder class="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 monochrome:text-white" />
                    </div>
                    <span class="text-sm font-bold">Move to Folder</span>
                </div>
            </button>

            {#if !item.is_folder}
                <button 
                    onclick={() => handleAction('download')}
                    class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
                >
                    <div class="flex items-center space-x-3">
                        <Download class="w-4 h-4 text-slate-400 group-hover:text-indigo-600 monochrome:text-white/60 monochrome:group-hover:text-white transition-colors icon-bounce" />
                        <span class="text-sm font-bold">Download</span>
                    </div>
                </button>
            {/if}

            <div class="h-px bg-slate-100 dark:bg-slate-800 monochrome:bg-white/10 my-2 mx-2"></div>

            <div>
                <button 
                    onclick={() => showCategories = !showCategories}
                    class={cn(
                        "w-full flex items-center justify-between px-3 py-2.5 rounded-xl transition-all group hover:translate-x-1 active:scale-95",
                        showCategories ? "bg-indigo-50 dark:bg-indigo-900/20 monochrome:bg-white/10 text-indigo-600 monochrome:text-white" : "hover:bg-indigo-50 dark:hover:bg-indigo-900/20 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white"
                    )}
                >
                    <div class="flex items-center space-x-3">
                        <Tag class="w-4 h-4 text-slate-400 group-hover:text-indigo-600 monochrome:text-white/60 monochrome:group-hover:text-white icon-bounce" />
                        <span class="text-sm font-bold">Move to Category</span>
                    </div>
                    <ChevronRight class={cn("w-3.5 h-3.5 transition-transform duration-200", showCategories && "rotate-90")} />
                </button>

                {#if showCategories}
                    <div 
                        class="mt-1 space-y-0.5 bg-slate-50 dark:bg-slate-800/30 monochrome:bg-white/5 rounded-xl p-1 mx-1 border border-slate-100 dark:border-slate-800 monochrome:border-white/10"
                        transition:slide={{ duration: 200 }}
                    >
                        {#each categories as cat}
                            <button 
                                onclick={() => handleAction('category', { name: cat.name, id: cat.id })}
                                class="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-600 dark:text-slate-300 monochrome:text-white transition-all hover:translate-x-1 active:scale-95 group"
                            >
                                <div class={cn("w-2 h-2 rounded-full", cat.color)}></div>
                                <span class="text-xs font-bold text-left">{cat.name}</span>
                            </button>
                        {/each}
                        <button 
                            onclick={() => handleAction('category', { name: null, id: null })}
                            class="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-slate-800 monochrome:hover:bg-white/10 text-slate-500 monochrome:text-white/60 transition-all hover:translate-x-1 active:scale-95"
                        >
                            <div class="w-2 h-2 rounded-full bg-slate-200 dark:bg-slate-700 monochrome:bg-white/20"></div>
                            <span class="text-xs font-bold uppercase tracking-widest text-left">None</span>
                        </button>
                    </div>
                {/if}
            </div>

            <div class="h-px bg-slate-100 dark:bg-slate-800 monochrome:bg-white/10 my-2 mx-2"></div>

            <button 
                onclick={() => handleAction('trash')}
                class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-rose-50 dark:hover:bg-rose-900/20 monochrome:hover:bg-white/10 text-rose-600 dark:text-rose-400 monochrome:text-white transition-all group hover:translate-x-1 active:scale-95"
            >
                <div class="flex items-center space-x-3">
                    <Trash2 class="w-4 h-4 text-rose-400 group-hover:text-rose-600 icon-bounce" />
                    <span class="text-sm font-bold">Move to Trash</span>
                </div>
            </button>
        {/if}
    </div>
</div>
