<script lang="ts">
    import { toasts, type Toast } from '$lib/toasts';
    import { fade, fly } from 'svelte/transition';
    import { CheckCircle, XCircle, Info, X } from 'lucide-svelte';
    import { cn } from '$lib/utils';

    let allToasts = $derived($toasts);
</script>

<div class="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 w-full max-w-sm">
    {#each allToasts as toast (toast.id)}
        <div 
            in:fly={{ x: 100, duration: 400 }}
            out:fade={{ duration: 200 }}
            class={cn(
                "flex items-center justify-between p-4 rounded-2xl shadow-xl border backdrop-blur-md",
                toast.type === 'success' && "bg-emerald-50/90 border-emerald-100 text-emerald-800 dark:bg-emerald-950/90 dark:border-emerald-900 dark:text-emerald-300",
                toast.type === 'error' && "bg-rose-50/90 border-rose-100 text-rose-800 dark:bg-rose-950/90 dark:border-rose-900 dark:text-rose-300",
                toast.type === 'info' && "bg-indigo-50/90 border-indigo-100 text-indigo-800 dark:bg-indigo-950/90 dark:border-indigo-900 dark:text-indigo-300"
            )}
        >
            <div class="flex items-center space-x-3">
                {#if toast.type === 'success'}
                    <CheckCircle class="w-5 h-5" />
                {:else if toast.type === 'error'}
                    <XCircle class="w-5 h-5" />
                {:else}
                    <Info class="w-5 h-5" />
                {/if}
                <p class="text-sm font-semibold">{toast.message}</p>
            </div>
            <button onclick={() => toasts.remove(toast.id)} class="p-1 hover:bg-black/5 rounded-lg transition-colors">
                <X class="w-4 h-4" />
            </button>
        </div>
    {/each}
</div>
