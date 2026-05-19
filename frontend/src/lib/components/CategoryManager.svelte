<script lang="ts">
    import { X, Plus, Trash2, Tag, Palette } from 'lucide-svelte';
    import api from '$lib/api';
    import { cn } from '$lib/utils';
    import { fade, fly, slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { toasts } from '$lib/toasts';

    let { onclose } = $props<{ onclose: () => void }>();

    let categories = $state<any[]>([]);
    let loading = $state(true);
    let newName = $state('');
    let selectedColor = $state('bg-indigo-500');

    const colors = [
        'bg-indigo-500', 'bg-rose-500', 'bg-emerald-500', 
        'bg-amber-500', 'bg-sky-500', 'bg-violet-500', 
        'bg-fuchsia-500', 'bg-slate-500'
    ];

    async function fetchCategories() {
        try {
            const response = await api.get('/categories/');
            categories = response.data;
        } catch (e) {
            toasts.error('Failed to load categories');
        } finally {
            loading = false;
        }
    }

    async function addCategory() {
        if (!newName) return;
        try {
            const response = await api.post('/categories/', {
                name: newName,
                color: selectedColor
            });
            categories = [...categories, response.data];
            newName = '';
            toasts.success('Category created');
        } catch (e) {
            toasts.error('Failed to create category');
        }
    }

    async function deleteCategory(id: string) {
        try {
            await api.delete(`/categories/${id}`);
            categories = categories.filter(c => c.id !== id);
            toasts.info('Category removed');
        } catch (e) {
            toasts.error('Failed to delete category');
        }
    }

    fetchCategories();
</script>

<div 
    class="fixed inset-0 bg-slate-900/60 dark:bg-[#020617]/80 backdrop-blur-md flex items-center justify-center z-[70] p-6"
    transition:fade={{ duration: 200 }}
    onclick={onclose}
>
    <div 
        class="bg-white dark:bg-slate-900 rounded-[40px] p-8 w-full max-w-md shadow-2xl border border-white/20 dark:border-slate-800 relative overflow-hidden"
        transition:fly={{ y: 40, duration: 400, easing: quintOut }}
        onclick={(e) => e.stopPropagation()}
    >
        <div class="flex items-center justify-between mb-8">
            <div class="flex items-center space-x-4">
                <div class="bg-amber-100 dark:bg-amber-900/40 p-2.5 rounded-2xl">
                    <Tag class="w-6 h-6 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                    <h2 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">Manage Categories</h2>
                    <p class="text-slate-400 text-xs font-bold uppercase tracking-widest">Custom Organization</p>
                </div>
            </div>
            <button onclick={onclose} class="p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-slate-400 transition-all">
                <X class="w-5 h-5" />
            </button>
        </div>

        <div class="space-y-6">
            <!-- Create New -->
            <div class="space-y-4">
                <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">New Label</label>
                <div class="flex flex-col space-y-3">
                    <input 
                        bind:value={newName} 
                        type="text" 
                        placeholder="Project X, Marketing, etc." 
                        class="w-full bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-2xl px-5 py-3 text-sm font-bold focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/30 transition-all outline-none text-slate-700 dark:text-slate-200" 
                    />
                    <div class="flex items-center justify-between">
                        <div class="flex space-x-2">
                            {#each colors as color}
                                <button 
                                    onclick={() => selectedColor = color}
                                    class={cn(
                                        "w-6 h-6 rounded-full transition-all ring-offset-2 dark:ring-offset-slate-900",
                                        color,
                                        selectedColor === color ? "ring-2 ring-indigo-500 scale-110" : "hover:scale-110"
                                    )}
                                ></button>
                            {/each}
                        </div>
                        <button 
                            onclick={addCategory} 
                            disabled={!newName}
                            class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl text-xs font-black transition-all active:scale-95 shadow-lg shadow-indigo-200 dark:shadow-none"
                        >
                            CREATE
                        </button>
                    </div>
                </div>
            </div>

            <div class="h-px bg-slate-100 dark:bg-slate-800"></div>

            <!-- List Existing -->
            <div class="space-y-3">
                <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Active Categories</label>
                <div class="max-h-60 overflow-y-auto custom-scrollbar space-y-2 pr-2">
                    {#if loading}
                        <div class="space-y-2">
                            {#each Array(3) as _}
                                <div class="h-12 bg-slate-50 dark:bg-slate-800/30 rounded-2xl animate-pulse"></div>
                            {/each}
                        </div>
                    {:else if categories.length === 0}
                        <p class="text-center py-8 text-xs font-bold text-slate-400 uppercase tracking-widest italic">No custom categories yet</p>
                    {:else}
                        {#each categories as cat}
                            <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-transparent hover:border-slate-100 dark:hover:border-slate-700 transition-all group" in:slide>
                                <div class="flex items-center space-x-3">
                                    <div class={cn("w-3 h-3 rounded-full shadow-sm", cat.color)}></div>
                                    <span class="text-sm font-bold text-slate-700 dark:text-slate-200 tracking-tight">{cat.name}</span>
                                </div>
                                <button onclick={() => deleteCategory(cat.id)} class="p-2 text-slate-300 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-xl transition-all opacity-0 group-hover:opacity-100">
                                    <Trash2 class="w-4 h-4" />
                                </button>
                            </div>
                        {/each}
                    {/if}
                </div>
            </div>
        </div>
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
