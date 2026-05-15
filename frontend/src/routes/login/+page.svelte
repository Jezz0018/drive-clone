<script lang="ts">
    import api from '$lib/api';
    import { token, user } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { Cloud, Lock, Mail, ArrowRight, Sun, Moon } from 'lucide-svelte';
    import { fade, fly } from 'svelte/transition';
    import { toasts } from '$lib/toasts';
    import { theme } from '$lib/theme.svelte';
    import { cn } from '$lib/utils';

    let email = $state('');
    let password = $state('');
    let loading = $state(false);

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        loading = true;
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const response = await api.post('/auth/login/access-token', formData);
            token.set(response.data.access_token);
            
            const userResponse = await api.get('/auth/me');
            user.set(userResponse.data);
            
            toasts.success('Access granted to DRIVE X');
            goto('/');
        } catch (e: any) {
            toasts.error(e.response?.data?.detail || 'Authentication failed');
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Sign In | DRIVE X</title>
</svelte:head>

<div class="min-h-screen w-full flex items-center justify-center p-6 bg-slate-50 dark:bg-[#020617] transition-colors duration-500 relative overflow-hidden">
    <!-- Background Accents -->
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-[120px]"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/10 dark:bg-indigo-600/5 rounded-full blur-[120px]"></div>

    <!-- Theme Toggle -->
    <div class="absolute top-8 right-8">
        <button 
            onclick={() => theme.toggle()}
            class="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm hover:shadow-md transition-all text-slate-500 dark:text-slate-400"
        >
            {#if theme.current === 'light'}
                <Moon class="w-5 h-5" />
            {:else}
                <Sun class="w-5 h-5" />
            {/if}
        </button>
    </div>

    <div 
        class="w-full max-w-md z-10"
        in:fly={{ y: 20, duration: 800 }}
    >
        <!-- Logo -->
        <div class="flex flex-col items-center mb-10">
            <div class="bg-indigo-600 p-4 rounded-[28px] shadow-2xl shadow-indigo-200 dark:shadow-none mb-4 group cursor-default transition-transform duration-500 hover:rotate-12">
                <Cloud class="w-10 h-10 text-white" />
            </div>
            <h1 class="text-3xl font-black tracking-tighter text-slate-900 dark:text-white">
                DRIVE <span class="text-indigo-600">X</span>
            </h1>
            <p class="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mt-2">Sign In</p>
        </div>

        <!-- Login Card -->
        <div class="bg-white/80 dark:bg-[#0f172a]/60 backdrop-blur-2xl p-10 rounded-[40px] border border-white dark:border-slate-800 shadow-2xl shadow-slate-200/50 dark:shadow-none">
            <div class="mb-8">
                <h2 class="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Welcome Back</h2>
                <p class="text-slate-500 dark:text-slate-400 font-medium text-sm mt-1">Access your secure cloud drive</p>
            </div>

            <form class="space-y-6" onsubmit={handleSubmit}>
                <div class="space-y-5">
                    <div class="space-y-2">
                        <label for="email" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Email Address</label>
                        <div class="relative group">
                            <Mail class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input 
                                id="email" 
                                bind:value={email} 
                                type="email" 
                                required 
                                placeholder="name@company.com"
                                class="w-full pl-14 pr-6 py-4 bg-slate-50/50 dark:bg-slate-900/50 border-2 border-slate-100 dark:border-slate-800 rounded-[22px] focus:bg-white dark:focus:bg-slate-900 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none text-slate-700 dark:text-slate-200 font-bold text-sm" 
                            />
                        </div>
                    </div>
                    
                    <div class="space-y-2">
                        <div class="flex justify-between items-center ml-1">
                            <label for="password" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Password</label>
                            <button type="button" class="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest hover:underline bg-transparent border-none p-0 cursor-pointer">Reset</button>
                        </div>
                        <div class="relative group">
                            <Lock class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input 
                                id="password" 
                                bind:value={password} 
                                type="password" 
                                required 
                                placeholder="••••••••"
                                class="w-full pl-14 pr-6 py-4 bg-slate-50/50 dark:bg-slate-900/50 border-2 border-slate-100 dark:border-slate-800 rounded-[22px] focus:bg-white dark:focus:bg-slate-900 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none text-slate-700 dark:text-slate-200 font-bold text-sm" 
                            />
                        </div>
                    </div>
                </div>

                <button 
                    type="submit" 
                    disabled={loading} 
                    class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-[22px] py-4 shadow-xl shadow-indigo-100 dark:shadow-none transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center space-x-2 text-lg tracking-tight group"
                >
                    {#if loading}
                        <div class="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    {:else}
                        <span>Sign In</span>
                        <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    {/if}
                </button>
            </form>

            <div class="mt-10 pt-8 border-t border-slate-100 dark:border-slate-800 text-center">
                <p class="text-sm font-bold text-slate-400 dark:text-slate-500">
                    New to the network? 
                    <a href="/signup" class="text-indigo-600 dark:text-indigo-400 hover:underline ml-1">Create Account</a>
                </p>
            </div>
        </div>
        
        <!-- Subtle Footer -->
        <p class="mt-8 text-center text-[10px] font-bold text-slate-300 dark:text-slate-700 uppercase tracking-[0.4em]">
            SYSTEM VERSION 2.0.4 - SECURE NODE
        </p>
    </div>
</div>
