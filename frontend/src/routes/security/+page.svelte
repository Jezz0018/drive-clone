<script lang="ts">
    import Header from '$lib/components/Header.svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import { ShieldCheck, Lock, Eye, Key } from 'lucide-svelte';
    import { fly } from 'svelte/transition';
    import { toasts } from '$lib/toasts';
</script>

<svelte:head>
    <title>Security & Privacy | DRIVE X</title>
</svelte:head>

<div class="h-screen flex flex-col">
    <Header />
    <div class="flex-1 flex overflow-hidden">
        <Sidebar activeView="security" />
        
        <main class="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#0f172a] p-8 custom-scrollbar">
            <div class="max-w-4xl mx-auto space-y-8" in:fly={{ y: 20, duration: 600 }}>
                <!-- Page Header -->
                <div>
                    <div class="flex items-center space-x-2 text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-3">
                        <ShieldCheck class="w-3 h-3" />
                        <span>Account Protection</span>
                    </div>
                    <h1 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">Security & Privacy</h1>
                </div>

                <div class="bg-white dark:bg-slate-900 rounded-[40px] border border-slate-200/50 dark:border-slate-800 shadow-sm overflow-hidden p-10">
                    <div class="space-y-12">
                        <!-- Identity Section -->
                        <div class="space-y-6">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center space-x-4">
                                    <div class="p-3 rounded-2xl bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600">
                                        <ShieldCheck class="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 class="text-lg font-bold text-slate-900 dark:text-white">Multi-Factor Authentication</h3>
                                        <p class="text-xs text-slate-500 font-medium">Verify your identity with secure challenges</p>
                                    </div>
                                </div>
                                <span class="bg-emerald-100 text-emerald-600 px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-widest">Active</span>
                            </div>
                            <div class="p-6 rounded-3xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50">
                                <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">Your account is secured with email OTP verification and cryptographic math challenges. All access attempts are monitored and recorded for system integrity.</p>
                            </div>
                        </div>

                        <!-- Data Protection -->
                        <div class="space-y-6">
                            <div class="flex items-center space-x-4">
                                <div class="p-3 rounded-2xl bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600">
                                    <Lock class="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">End-to-End Encryption</h3>
                                    <p class="text-xs text-slate-500 font-medium">Server-side encryption protocols</p>
                                </div>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 flex items-center space-x-3">
                                    <Key class="w-4 h-4 text-indigo-500" />
                                    <span class="text-sm font-bold text-slate-700 dark:text-slate-200">AES-256 Storage Encryption</span>
                                </div>
                                <div class="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 flex items-center space-x-3">
                                    <Eye class="w-4 h-4 text-rose-500" />
                                    <span class="text-sm font-bold text-slate-700 dark:text-slate-200">Private Data Isolation</span>
                                </div>
                            </div>
                        </div>

                        <!-- Privacy Controls -->
                        <div class="space-y-6">
                            <h3 class="text-lg font-bold text-slate-900 dark:text-white">Privacy Preferences</h3>
                            <div class="space-y-3">
                                <label class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 cursor-pointer hover:bg-slate-100 transition-all">
                                    <div class="flex flex-col">
                                        <span class="text-sm font-bold text-slate-700 dark:text-slate-200">Visible to team</span>
                                        <span class="text-[10px] text-slate-500">Allow collaborators to see your online status</span>
                                    </div>
                                    <input type="checkbox" checked class="w-5 h-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                                </label>
                                <label class="flex items-center justify-between p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 cursor-pointer hover:bg-slate-100 transition-all">
                                    <div class="flex flex-col">
                                        <span class="text-sm font-bold text-slate-700 dark:text-slate-200">System Analytics</span>
                                        <span class="text-[10px] text-slate-500">Anonymous data collection for system optimization</span>
                                    </div>
                                    <input type="checkbox" class="w-5 h-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
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
