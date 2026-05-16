<script lang="ts">
    import { onMount } from 'svelte';
    import api from '$lib/api';
    import { goto } from '$app/navigation';
    import { Cloud, User, Mail, Lock, ArrowRight, Sun, Moon, Phone, ShieldCheck, MailCheck, RefreshCw } from 'lucide-svelte';
    import { fade, fly, slide } from 'svelte/transition';
    import { toasts } from '$lib/toasts';
    import { theme } from '$lib/theme.svelte';
    import { cn } from '$lib/utils';

    let email = $state('');
    let password = $state('');
    let fullName = $state('');
    let phoneNumber = $state('');
    let loading = $state(false);
    
    // Verification State
    let step = $state<'signup' | 'verify'>('signup');
    let otpCode = $state('');

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        loading = true;
        try {
            await api.post('/auth/signup', {
                email,
                password,
                full_name: fullName,
                phone_number: phoneNumber
            });
            toasts.success('Verification code sent to your email.');
            step = 'verify';
        } catch (e: any) {
            toasts.error(e.response?.data?.detail || 'Account creation failed');
        } finally {
            loading = false;
        }
    }

    async function handleVerify(e: SubmitEvent) {
        e.preventDefault();
        loading = true;
        try {
            await api.post('/auth/verify-otp', {
                email,
                code: otpCode
            });
            toasts.success('Account verified! You may now sign in.');
            goto('/login');
        } catch (e: any) {
            toasts.error(e.response?.data?.detail || 'Verification failed');
        } finally {
            loading = false;
        }
    }

    async function resendOTP() {
        loading = true;
        try {
            // Re-call signup with same data to trigger new OTP
            await api.post('/auth/signup', {
                email,
                password,
                full_name: fullName,
                phone_number: phoneNumber
            });
            toasts.info('New verification code sent.');
            otpCode = '';
        } catch (e) {
            toasts.error('Failed to resend code.');
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>{step === 'signup' ? 'Create Account' : 'Verify Email'} | DRIVE X</title>
</svelte:head>

<div class="min-h-screen w-full flex items-center justify-center p-6 bg-slate-50 dark:bg-[#020617] transition-colors duration-500 relative overflow-hidden">
    <!-- Background Accents -->
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-[120px]"></div>
    <div class="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-violet-500/10 dark:bg-indigo-600/5 rounded-full blur-[120px]"></div>

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
            <div class="bg-indigo-600 p-4 rounded-[28px] shadow-2xl shadow-indigo-200 dark:shadow-none mb-4 group cursor-default transition-transform duration-500 hover:-rotate-12">
                <Cloud class="w-10 h-10 text-white" />
            </div>
            <h1 class="text-3xl font-black tracking-tighter text-slate-900 dark:text-white">
                DRIVE <span class="text-indigo-600">X</span>
            </h1>
            <p class="text-sm font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mt-2">
                {step === 'signup' ? 'Create Account' : 'Verify Identity'}
            </p>
        </div>

        <!-- Card -->
        <div class="bg-white/80 dark:bg-[#0f172a]/60 backdrop-blur-2xl p-10 rounded-[40px] border border-white dark:border-slate-800 shadow-2xl shadow-slate-200/50 dark:shadow-none relative">
            {#if step === 'signup'}
                <div in:fade>
                    <div class="mb-8 text-center lg:text-left">
                        <h2 class="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Register User</h2>
                        <p class="text-slate-500 dark:text-slate-400 font-medium text-sm mt-1">Join the secure cloud network</p>
                    </div>

                    <form class="space-y-5" onsubmit={handleSubmit}>
                        <div class="space-y-4">
                            <div class="space-y-2">
                                <label for="fullName" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Full Name</label>
                                <div class="relative group">
                                    <User class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                    <input 
                                        id="fullName" 
                                        bind:value={fullName} 
                                        type="text" 
                                        required 
                                        placeholder="John Doe"
                                        class="w-full pl-14 pr-6 py-4 bg-slate-50/50 dark:bg-slate-900/50 border-2 border-slate-100 dark:border-slate-800 rounded-[22px] focus:bg-white dark:focus:bg-slate-900 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none text-slate-700 dark:text-slate-200 font-bold text-sm" 
                                    />
                                </div>
                            </div>
                            
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
                                <label for="phone" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Phone Number</label>
                                <div class="relative group">
                                    <Phone class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                    <input 
                                        id="phone" 
                                        bind:value={phoneNumber} 
                                        type="tel" 
                                        required 
                                        placeholder="+1 (555) 000-0000"
                                        class="w-full pl-14 pr-6 py-4 bg-slate-50/50 dark:bg-slate-900/50 border-2 border-slate-100 dark:border-slate-800 rounded-[22px] focus:bg-white dark:focus:bg-slate-900 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none text-slate-700 dark:text-slate-200 font-bold text-sm" 
                                    />
                                </div>
                            </div>

                            <div class="space-y-2">
                                <label for="password" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Security Password</label>
                                <div class="relative group">
                                    <Lock class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                    <input 
                                        id="password" 
                                        bind:value={password} 
                                        type="password" 
                                        required 
                                        placeholder="Min. 8 characters"
                                        class="w-full pl-14 pr-6 py-4 bg-slate-50/50 dark:bg-slate-900/50 border-2 border-slate-100 dark:border-slate-800 rounded-[22px] focus:bg-white dark:focus:bg-slate-900 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none text-slate-700 dark:text-slate-200 font-bold text-sm" 
                            />
                                </div>
                            </div>
                        </div>

                        <div class="flex items-start space-x-3 py-2 ml-1">
                            <input type="checkbox" id="terms" required class="mt-1 rounded text-indigo-600 focus:ring-indigo-500 h-4 w-4 bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700" />
                            <label for="terms" class="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-tighter leading-relaxed">
                                I agree to the <button type="button" class="text-indigo-600 dark:text-indigo-400 underline p-0 bg-transparent border-none cursor-pointer font-bold">Terms</button> and <button type="button" class="text-indigo-600 dark:text-indigo-400 underline p-0 bg-transparent border-none cursor-pointer font-bold">Privacy Policy</button>
                            </label>
                        </div>

                        <button 
                            type="submit" 
                            disabled={loading} 
                            class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-[22px] py-4 shadow-xl shadow-indigo-100 dark:shadow-none transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center space-x-2 text-lg tracking-tight group"
                        >
                            {#if loading}
                                <div class="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                            {:else}
                                <span>Continue</span>
                                <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            {/if}
                        </button>
                    </form>
                </div>
            {:else}
                <div in:fade>
                    <div class="mb-10 text-center">
                        <div class="bg-emerald-100 dark:bg-emerald-900/30 w-16 h-16 rounded-[24px] flex items-center justify-center mx-auto mb-4">
                            <MailCheck class="w-8 h-8 text-emerald-600" />
                        </div>
                        <h2 class="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Check your email</h2>
                        <p class="text-slate-500 dark:text-slate-400 font-medium text-sm mt-2 px-4">
                            We've sent a 6-digit verification code to <span class="text-indigo-600 font-bold">{email}</span>
                        </p>
                    </div>

                    <form class="space-y-8" onsubmit={handleVerify}>
                        <div class="space-y-4">
                            <div class="space-y-2">
                                <label for="otp" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest text-center">Verification Code</label>
                                <div class="relative group">
                                    <ShieldCheck class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                    <input 
                                        id="otp" 
                                        bind:value={otpCode} 
                                        type="text" 
                                        maxlength="6"
                                        required 
                                        placeholder="0 0 0 0 0 0"
                                        class="w-full pl-14 pr-6 py-5 bg-slate-50/50 dark:bg-slate-900/50 border-2 border-slate-100 dark:border-slate-800 rounded-[22px] focus:bg-white dark:focus:bg-slate-900 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all outline-none text-slate-700 dark:text-slate-200 font-black text-2xl tracking-[0.5em] text-center" 
                                    />
                                </div>
                            </div>
                        </div>

                        <div class="space-y-4">
                            <button 
                                type="submit" 
                                disabled={loading || otpCode.length < 6} 
                                class="w-full bg-slate-900 dark:bg-indigo-600 hover:bg-black dark:hover:bg-indigo-700 text-white font-black rounded-[22px] py-4 shadow-xl transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center space-x-2 text-lg tracking-tight"
                            >
                                {#if loading}
                                    <div class="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                                {:else}
                                    <span>Verify & Complete</span>
                                {/if}
                            </button>

                            <button 
                                type="button" 
                                onclick={resendOTP}
                                disabled={loading}
                                class="w-full flex items-center justify-center space-x-2 text-sm font-bold text-slate-400 hover:text-indigo-600 transition-colors bg-transparent border-none p-2"
                            >
                                <RefreshCw class={cn("w-4 h-4", loading && "animate-spin")} />
                                <span>Resend Code</span>
                            </button>
                        </div>
                    </form>

                    <button 
                        onclick={() => step = 'signup'} 
                        class="mt-6 w-full text-[10px] font-black text-slate-400 uppercase tracking-widest hover:text-slate-600 transition-colors"
                    >
                        Back to Signup
                    </button>
                </div>
            {/if}

            <div class="mt-10 pt-8 border-t border-slate-100 dark:border-slate-800 text-center">
                <p class="text-sm font-bold text-slate-400 dark:text-slate-500">
                    Already have an account? 
                    <a href="/login" class="text-indigo-600 dark:text-indigo-400 hover:underline ml-1">Sign In</a>
                </p>
            </div>
        </div>
    </div>
</div>
