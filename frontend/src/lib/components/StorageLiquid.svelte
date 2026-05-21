<script lang="ts">
    import { onMount } from 'svelte';
    import { storageUsage } from '$lib/stores';
    import { cn } from '$lib/utils';

    let percentage = $derived(Math.min(100, Math.round(($storageUsage.used / $storageUsage.limit) * 100)) || 0);
    let liquidHeight = $derived(100 - percentage);
</script>

<div class="relative w-full h-32 bg-slate-50 dark:bg-[#020617]/50 monochrome:bg-black rounded-[28px] border border-slate-200/50 dark:border-slate-800/50 monochrome:border-white/10 overflow-hidden group">
    <!-- Liquid Container -->
    <div 
        class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-indigo-600 to-indigo-500 dark:from-indigo-700 dark:to-indigo-500 monochrome:from-white monochrome:to-gray-300 transition-all duration-1000 ease-in-out"
        style="height: {percentage}%"
    >
        <!-- Wave Animation -->
        <div class="absolute -top-4 left-0 w-[200%] h-8 opacity-50 fill-indigo-500 monochrome:fill-white animate-wave-slow">
            <svg viewBox="0 0 1000 100" preserveAspectRatio="none" class="w-full h-full">
                <path d="M0,50 C150,100 350,0 500,50 C650,100 850,0 1000,50 L1000,100 L0,100 Z" />
            </svg>
        </div>
        <div class="absolute -top-3 left-0 w-[200%] h-8 opacity-30 dark:opacity-20 monochrome:opacity-30 fill-white monochrome:fill-black animate-wave-fast translate-x-[-25%]">
            <svg viewBox="0 0 1000 100" preserveAspectRatio="none" class="w-full h-full">
                <path d="M0,50 C150,100 350,0 500,50 C650,100 850,0 1000,50 L1000,100 L0,100 Z" />
            </svg>
        </div>

        <!-- Bubbles -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
            {#each Array(5) as _, i}
                <div 
                    class="absolute w-1 h-1 bg-white/30 rounded-full animate-bubble"
                    style="left: {20 * i + 10}%; bottom: -10px; animation-delay: {i * 0.5}s; animation-duration: {3 + i}s"
                ></div>
            {/each}
        </div>
    </div>

    <!-- Center Info -->
    <div class="absolute inset-0 flex flex-col items-center justify-center z-10">
        <span class={cn(
            "text-3xl font-black tracking-tighter transition-colors duration-500",
            percentage > 60 ? "text-white" : "text-slate-900 dark:text-white"
        )}>
            {percentage}%
        </span>
        <span class={cn(
            "text-[8px] font-black uppercase tracking-[0.2em] transition-colors duration-500",
            percentage > 60 ? "text-indigo-100" : "text-slate-400 dark:text-slate-500"
        )}>
            Storage Used
        </span>
    </div>

    <!-- Glass Reflections -->
    <div class="absolute inset-0 pointer-events-none border border-white/20 dark:border-white/5 rounded-[28px]"></div>
    <div class="absolute top-2 left-4 w-12 h-1 bg-white/20 rounded-full blur-[1px]"></div>
</div>

<style>
    @keyframes wave {
        from { transform: translateX(0); }
        to { transform: translateX(-50%); }
    }

    .animate-wave-slow {
        animation: wave 10s linear infinite;
    }

    .animate-wave-fast {
        animation: wave 7s linear infinite;
    }

    @keyframes bubble {
        0% { transform: translateY(0) scale(1); opacity: 0; }
        20% { opacity: 0.5; }
        100% { transform: translateY(-100px) scale(1.5); opacity: 0; }
    }

    .animate-bubble {
        animation: bubble linear infinite;
    }
</style>
