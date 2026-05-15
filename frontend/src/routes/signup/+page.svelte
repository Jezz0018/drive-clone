<script lang="ts">
    import api from '$lib/api';
    import { goto } from '$app/navigation';
    import { Cloud, User, Mail, Lock, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-svelte';
    import { fade, fly } from 'svelte/transition';
    import { toasts } from '$lib/toasts';

    let email = $state('');
    let password = $state('');
    let fullName = $state('');
    let error = $state('');
    let loading = $state(false);

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        loading = true;
        error = '';
        try {
            await api.post('/auth/signup', {
                email,
                password,
                full_name: fullName
            });
            toasts.success('Account created successfully! Please sign in.');
            goto('/login');
        } catch (e: any) {
            error = e.response?.data?.detail || 'Signup failed. Please try again.';
            toasts.error(error);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Create Account | JS Vault</title>
</svelte:head>

<div class="min-h-screen flex bg-white dark:bg-[#0f172a] overflow-hidden transition-colors duration-300">
    <!-- Left: Signup Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 md:p-16 relative">
        <div class="max-w-md w-full" in:fly={{ x: -50, duration: 600 }}>
            <div class="mb-10 text-center lg:text-left">
                <div class="lg:hidden flex justify-center mb-6">
                    <div class="bg-indigo-600 p-2 rounded-2xl shadow-lg">
                        <Cloud class="w-8 h-8 text-white" />
                    </div>
                </div>
                <h2 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter mb-2">Create Account</h2>
                <p class="text-slate-500 dark:text-slate-400 font-medium">Join JS Vault today and start securing your assets.</p>
            </div>

            <form class="space-y-5" onsubmit={handleSubmit}>
                <div class="space-y-4">
                    <div>
                        <label for="fullName" class="block text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-2">Full Name</label>
                        <div class="relative group">
                            <User class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input 
                                id="fullName" 
                                bind:value={fullName} 
                                type="text" 
                                required 
                                placeholder="John Doe"
                                class="w-full pl-12 pr-4 py-4 bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-2xl focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-50 dark:focus:ring-indigo-900/10 transition-all outline-none text-slate-700 dark:text-slate-200 font-semibold" 
                            />
                        </div>
                    </div>
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
                        <label for="password" class="block text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-2">Password</label>
                        <div class="relative group">
                            <Lock class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input 
                                id="password" 
                                bind:value={password} 
                                type="password" 
                                required 
                                placeholder="Min. 8 characters"
                                class="w-full pl-12 pr-4 py-4 bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-2xl focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-50 dark:focus:ring-indigo-900/10 transition-all outline-none text-slate-700 dark:text-slate-200 font-semibold" 
                            />
                        </div>
                    </div>
                </div>

                <div class="flex items-start space-x-3 py-2">
                    <input type="checkbox" id="terms" required class="mt-1 rounded text-indigo-600 focus:ring-indigo-500 h-4 w-4" />
                    <label for="terms" class="text-xs text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
                        By creating an account, you agree to our <a href="#" class="text-indigo-600 dark:text-indigo-400 underline">Terms of Service</a> and <a href="#" class="text-indigo-600 dark:text-indigo-400 underline">Privacy Policy</a>.
                    </label>
                </div>

                <button 
                    type="submit" 
                    disabled={loading} 
                    class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-2xl py-4 shadow-xl shadow-indigo-100 dark:shadow-none transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center space-x-2 text-lg tracking-tight"
                >
                    {#if loading}
                        <div class="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                        <span>Creating Account...</span>
                    {:else}
                        <span>Initialize Vault</span>
                        <ArrowRight class="w-5 h-5" />
                    {/if}
                </button>
            </form>

            <p class="mt-10 text-center text-sm font-bold text-slate-500 dark:text-slate-400">
                Already have a vault? 
                <a href="/login" class="text-indigo-600 dark:text-indigo-400 hover:underline">Sign in instead</a>
            </p>
        </div>
    </div>

    <!-- Right: Features Showcase (Hidden on Mobile) -->
    <div class="hidden lg:flex lg:w-1/2 bg-slate-900 relative overflow-hidden flex-col justify-center p-16 text-white transition-colors duration-300">
        <div class="relative z-10 max-w-lg">
            <h3 class="text-4xl font-black mb-8 tracking-tighter">Why thousands of developers <br />trust <span class="text-indigo-400 underline decoration-4 decoration-indigo-400/30 underline-offset-8">JS Vault.</span></h3>
            
            <div class="space-y-8">
                <div class="flex items-start space-x-4">
                    <div class="bg-indigo-500/10 p-2.5 rounded-xl border border-indigo-500/20">
                        <CheckCircle2 class="w-6 h-6 text-indigo-400" />
                    </div>
                    <div>
                        <h4 class="font-black text-lg text-indigo-100">Zero-Knowledge Architecture</h4>
                        <p class="text-slate-400 text-sm font-medium">We can't see your data. Even if we wanted to. Your private keys stay on your machine.</p>
                    </div>
                </div>
                <div class="flex items-start space-x-4">
                    <div class="bg-emerald-500/10 p-2.5 rounded-xl border border-emerald-500/20">
                        <CheckCircle2 class="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                        <h4 class="font-black text-lg text-emerald-100">Smart Asset Management</h4>
                        <p class="text-slate-400 text-sm font-medium">Automatic categorization, deep search, and lightning-fast previews for all asset types.</p>
                    </div>
                </div>
                <div class="flex items-start space-x-4">
                    <div class="bg-amber-500/10 p-2.5 rounded-xl border border-amber-500/20">
                        <CheckCircle2 class="w-6 h-6 text-amber-400" />
                    </div>
                    <div>
                        <h4 class="font-black text-lg text-amber-100">Enterprise Scale</h4>
                        <p class="text-slate-400 text-sm font-medium">Scale from 1GB to 100TB with zero downtime and collaborative features built-in.</p>
                    </div>
                </div>
            </div>

            <!-- Dashboard Preview UI Mockup -->
            <div class="mt-12 p-6 bg-slate-800/50 rounded-3xl border border-slate-700/50 shadow-2xl backdrop-blur-xl animate-slide-up">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex space-x-1.5">
                        <div class="w-2 h-2 rounded-full bg-rose-500/50"></div>
                        <div class="w-2 h-2 rounded-full bg-amber-500/50"></div>
                        <div class="w-2 h-2 rounded-full bg-emerald-500/50"></div>
                    </div>
                    <div class="h-1 w-24 bg-slate-700 rounded-full"></div>
                </div>
                <div class="grid grid-cols-3 gap-3">
                    <div class="h-20 bg-indigo-500/20 rounded-2xl border border-indigo-500/10 flex items-center justify-center">
                        <Cloud class="w-6 h-6 text-indigo-400 opacity-50" />
                    </div>
                    <div class="h-20 bg-slate-700/50 rounded-2xl border border-slate-600/30"></div>
                    <div class="h-20 bg-slate-700/50 rounded-2xl border border-slate-600/30"></div>
                </div>
            </div>
        </div>

        <!-- Background patterns -->
        <div class="absolute inset-0 opacity-20" style="background-image: radial-gradient(circle at 2px 2px, #6366f1 1px, transparent 0); background-size: 40px 40px;"></div>
    </div>
</div>
