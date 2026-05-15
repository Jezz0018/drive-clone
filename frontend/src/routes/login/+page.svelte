<script lang="ts">
    import api from '$lib/api';
    import { token, user } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { Cloud, Lock, ShieldCheck, Zap, ArrowRight, Mail } from 'lucide-svelte';
    import { fade, fly, slide } from 'svelte/transition';
    import { toasts } from '$lib/toasts';

    let email = $state('');
    let password = $state('');
    let error = $state('');
    let loading = $state(false);

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        loading = true;
        error = '';
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const response = await api.post('/auth/login/access-token', formData);
            token.set(response.data.access_token);
            
            // Fetch user info
            const userResponse = await api.get('/auth/me');
            user.set(userResponse.data);
            
            toasts.success('Welcome back to your vault!');
            goto('/');
        } catch (e: any) {
            error = e.response?.data?.detail || 'Invalid credentials. Please try again.';
            toasts.error(error);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Sign In | JS Vault</title>
</svelte:head>

<div class="min-h-screen flex bg-white dark:bg-[#0f172a] overflow-hidden">
    <!-- Left: Branding & Benefits (Hidden on Mobile) -->
    <div class="hidden lg:flex lg:w-1/2 bg-indigo-600 relative overflow-hidden flex-col justify-between p-16 text-white">
        <div class="relative z-10">
            <div class="flex items-center space-x-3 mb-12">
                <div class="bg-white/20 p-2 rounded-2xl backdrop-blur-xl">
                    <Cloud class="w-8 h-8 text-white" />
                </div>
                <span class="text-2xl font-black tracking-tighter">JS <span class="text-indigo-200">VAULT</span></span>
            </div>
            
            <h1 class="text-6xl font-black leading-tight mb-8 tracking-tighter">
                Secure your digital <br />
                <span class="text-indigo-200">universe.</span>
            </h1>
            
            <div class="space-y-6">
                <div class="flex items-center space-x-4 group">
                    <div class="bg-white/10 p-3 rounded-2xl group-hover:bg-white/20 transition-colors">
                        <Lock class="w-6 h-6" />
                    </div>
                    <div>
                        <p class="font-bold text-lg">Military-grade Security</p>
                        <p class="text-indigo-100 text-sm">Your data is encrypted before it even leaves your device.</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4 group">
                    <div class="bg-white/10 p-3 rounded-2xl group-hover:bg-white/20 transition-colors">
                        <Zap class="w-6 h-6" />
                    </div>
                    <div>
                        <p class="font-bold text-lg">Lightning Fast Access</p>
                        <p class="text-indigo-100 text-sm">Instant synchronization across all your professional devices.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quote -->
        <div class="relative z-10 bg-white/10 backdrop-blur-xl p-8 rounded-[32px] border border-white/10 max-w-md">
            <p class="text-lg font-medium leading-relaxed italic mb-4">
                "The most intuitive digital storage experience I've used in years. It's clean, fast, and remarkably secure."
            </p>
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-full bg-indigo-400 flex items-center justify-center font-bold">JD</div>
                <div>
                    <p class="font-bold text-sm">Jane Doe</p>
                    <p class="text-indigo-200 text-xs font-bold uppercase tracking-widest">CTO at TechFlow</p>
                </div>
            </div>
        </div>

        <!-- Decorative elements -->
        <div class="absolute top-0 right-0 w-[600px] h-[600px] bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 translate-x-1/2 -translate-y-1/2"></div>
        <div class="absolute bottom-0 left-0 w-[400px] h-[400px] bg-violet-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 -translate-x-1/2 translate-y-1/2"></div>
    </div>

    <!-- Right: Login Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 md:p-16 relative">
        <div class="max-w-md w-full" in:fly={{ x: 50, duration: 600 }}>
            <div class="mb-10">
                <h2 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter mb-2">Welcome Back</h2>
                <p class="text-slate-500 dark:text-slate-400 font-medium">Please enter your credentials to access your vault.</p>
            </div>

            <form class="space-y-6" onsubmit={handleSubmit}>
                <div class="space-y-4">
                    <div>
                        <label for="email" class="block text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-2">Email Address</label>
                        <div class="relative group">
                            <Mail class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input 
                                id="email" 
                                bind:value={email} 
                                type="email" 
                                required 
                                placeholder="name@company.com"
                                class="w-full pl-12 pr-4 py-4 bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-2xl focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-50 dark:focus:ring-indigo-900/10 transition-all outline-none text-slate-700 dark:text-slate-200 font-semibold" 
                            />
                        </div>
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-2">
                            <label for="password" class="block text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Password</label>
                            <a href="#" class="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest hover:underline">Forgot password?</a>
                        </div>
                        <div class="relative group">
                            <Lock class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input 
                                id="password" 
                                bind:value={password} 
                                type="password" 
                                required 
                                placeholder="••••••••"
                                class="w-full pl-12 pr-4 py-4 bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-2xl focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-50 dark:focus:ring-indigo-900/10 transition-all outline-none text-slate-700 dark:text-slate-200 font-semibold" 
                            />
                        </div>
                    </div>
                </div>

                <button 
                    type="submit" 
                    disabled={loading} 
                    class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl py-4 shadow-xl shadow-indigo-100 dark:shadow-none transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center space-x-2 text-lg tracking-tight"
                >
                    {#if loading}
                        <div class="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                        <span>Verifying...</span>
                    {:else}
                        <span>Access Vault</span>
                        <ArrowRight class="w-5 h-5" />
                    {/if}
                </button>
            </form>

            <div class="mt-8 relative">
                <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-100 dark:border-slate-800"></div></div>
                <div class="relative flex justify-center text-xs uppercase font-black text-slate-300 dark:text-slate-600">
                    <span class="px-4 bg-white dark:bg-[#0f172a]">or continue with</span>
                </div>
            </div>

            <div class="mt-8 grid grid-cols-2 gap-4">
                <button class="flex items-center justify-center space-x-2 border-2 border-slate-100 dark:border-slate-800 rounded-2xl py-3 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-bold text-slate-600 dark:text-slate-300">
                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-4.5-2-7-2"></path></svg>
                    <span>GitHub</span>
                </button>
                <button class="flex items-center justify-center space-x-2 border-2 border-slate-100 dark:border-slate-800 rounded-2xl py-3 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors font-bold text-slate-600 dark:text-slate-300">
                    <img src="https://www.google.com/favicon.ico" class="w-4 h-4 grayscale opacity-70" alt="Google" />
                    <span>Google</span>
                </button>
            </div>

            <p class="mt-10 text-center text-sm font-bold text-slate-500 dark:text-slate-400">
                New to JS Vault? 
                <a href="/signup" class="text-indigo-600 dark:text-indigo-400 hover:underline">Create an account</a>
            </p>
        </div>

        <!-- Footer terms -->
        <div class="absolute bottom-8 text-center w-full max-w-md px-8">
            <p class="text-[10px] font-bold text-slate-300 dark:text-slate-600 uppercase tracking-widest">
                Protected by CloudShield Security © 2026 JS Vault
            </p>
        </div>
    </div>
</div>
