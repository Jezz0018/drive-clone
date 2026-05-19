<script lang="ts">
    import Header from '$lib/components/Header.svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import { user, token } from '$lib/stores';
    import { User, Mail, Phone, Calendar, ShieldCheck, LogOut, Settings as SettingsIcon, ChevronRight } from 'lucide-svelte';
    import { fly, fade } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { cn } from '$lib/utils';
    import { goto } from '$app/navigation';
    import { toasts } from '$lib/toasts';
    import api from '$lib/api';

    let showPasswordModal = $state(false);
    let oldPassword = $state('');
    let newPassword = $state('');
    let confirmPassword = $state('');
    let updating = $state(false);

    async function handleUpdatePassword() {
        if (newPassword !== confirmPassword) {
            toasts.error('Passwords do not match');
            return;
        }
        if (newPassword.length < 8) {
            toasts.error('Password must be at least 8 characters');
            return;
        }

        updating = true;
        try {
            await api.post('/auth/change-password', {
                old_password: oldPassword,
                new_password: newPassword
            });
            toasts.success('Password updated successfully');
            showPasswordModal = false;
            oldPassword = '';
            newPassword = '';
            confirmPassword = '';
        } catch (e: any) {
            toasts.error(e.response?.data?.detail || 'Failed to update password');
        } finally {
            updating = false;
        }
    }

    function handleLogout() {
        token.set(null);
        user.set(null);
        toasts.success('Logged out successfully');
        goto('/login');
    }
</script>

<svelte:head>
    <title>Profile Settings | DRIVE X</title>
</svelte:head>

<div class="h-screen flex flex-col">
    <Header />
    <div class="flex-1 flex overflow-hidden">
        <Sidebar activeView="profile" />
        
        <main class="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#0f172a] p-8 custom-scrollbar">
            <div class="max-w-4xl mx-auto space-y-8" in:fly={{ y: 20, duration: 600 }}>
                <!-- Page Header -->
                <div>
                    <div class="flex items-center space-x-2 text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-3">
                        <User class="w-3.5 h-3.5" />
                        <span>Identity Hub</span>
                    </div>
                    <h1 class="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">Profile Settings</h1>
                </div>

                <!-- Profile Card -->
                <div class="bg-white dark:bg-slate-900 rounded-[40px] border border-slate-200/50 dark:border-slate-800 shadow-sm overflow-hidden">
                    <!-- Banner -->
                    <div class="h-32 bg-indigo-600 relative">
                        <div class="absolute -bottom-12 left-10">
                            <div class="w-24 h-24 rounded-[32px] bg-white dark:bg-slate-800 p-2 shadow-xl">
                                <div class="w-full h-full rounded-[24px] bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center">
                                    <User class="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="pt-16 pb-10 px-10">
                        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                            <div>
                                <h2 class="text-2xl font-black text-slate-900 dark:text-white tracking-tight">{$user?.full_name || 'Anonymous User'}</h2>
                                <p class="text-slate-500 dark:text-slate-400 font-medium">Standard Active User</p>
                            </div>
                            <div class="flex items-center space-x-3">
                                <button 
                                    onclick={handleLogout}
                                    class="flex items-center space-x-2 px-6 py-3 bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 font-bold rounded-2xl hover:bg-rose-100 transition-all active:scale-95"
                                >
                                    <LogOut class="w-4 h-4" />
                                    <span>Sign Out</span>
                                </button>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
                            <!-- Info Section -->
                            <div class="space-y-6">
                                <h3 class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest border-b border-slate-100 dark:border-slate-800 pb-2">Account Information</h3>
                                
                                <div class="flex items-center space-x-4 group">
                                    <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 text-slate-400 group-hover:text-indigo-600 transition-colors">
                                        <Mail class="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p class="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Email Address</p>
                                        <p class="font-bold text-slate-700 dark:text-slate-200">{$user?.email}</p>
                                    </div>
                                </div>

                                <div class="flex items-center space-x-4 group">
                                    <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 text-slate-400 group-hover:text-indigo-600 transition-colors">
                                        <Phone class="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p class="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Phone Number</p>
                                        <p class="font-bold text-slate-700 dark:text-slate-200">{$user?.phone_number || 'Not provided'}</p>
                                    </div>
                                </div>

                                <div class="flex items-center space-x-4 group">
                                    <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 text-slate-400 group-hover:text-indigo-600 transition-colors">
                                        <Calendar class="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p class="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Member Since</p>
                                        <p class="font-bold text-slate-700 dark:text-slate-200">{new Date($user?.created_at).toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}</p>
                                    </div>
                                </div>
                            </div>

                            <!-- Quick Actions Section -->
                            <div class="space-y-6">
                                <h3 class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest border-b border-slate-100 dark:border-slate-800 pb-2">Quick Actions</h3>
                                
                                <button 
                                    class="w-full flex items-center justify-between p-5 rounded-[24px] bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 transition-all group"
                                    onclick={() => showPasswordModal = true}
                                >
                                    <div class="flex items-center space-x-3">
                                        <div class="w-2 h-2 rounded-full bg-indigo-500"></div>
                                        <span class="text-sm font-bold text-slate-700 dark:text-slate-200">Change Password</span>
                                    </div>
                                    <ChevronRight class="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
                                </button>

                                <button 
                                    class="w-full flex items-center justify-between p-5 rounded-[24px] bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 transition-all group"
                                    onclick={() => goto('/security')}
                                >
                                    <div class="flex items-center space-x-3">
                                        <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
                                        <span class="text-sm font-bold text-slate-700 dark:text-slate-200">Security Protocols</span>
                                    </div>
                                    <ChevronRight class="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- System Stats Footer -->
                <div class="flex items-center justify-center space-x-8 pt-4">
                    <div class="text-center">
                        <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Encrypted</p>
                        <div class="h-1 w-12 bg-indigo-500 rounded-full mx-auto"></div>
                    </div>
                    <div class="text-center">
                        <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Standard</p>
                        <div class="h-1 w-12 bg-slate-200 dark:bg-slate-700 rounded-full mx-auto"></div>
                    </div>
                    <div class="text-center">
                        <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Syncing</p>
                        <div class="h-1 w-12 bg-emerald-500 rounded-full mx-auto"></div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</div>

<!-- Password Change Modal -->
{#if showPasswordModal}
    <div 
        class="fixed inset-0 bg-slate-900/60 dark:bg-[#020617]/80 backdrop-blur-md flex items-center justify-center z-[70] p-6"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="bg-white dark:bg-slate-900 rounded-[48px] p-10 w-full max-w-md shadow-2xl border border-white/20 dark:border-slate-800 relative overflow-hidden"
            transition:fly={{ y: 40, duration: 400, easing: quintOut }}
        >
            <div class="mb-8">
                <h2 class="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Security Update</h2>
                <p class="text-slate-500 dark:text-slate-400 font-medium text-sm mt-1">Update your account credentials</p>
            </div>

            <div class="space-y-6">
                <div class="space-y-2">
                    <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Current Password</label>
                    <input 
                        bind:value={oldPassword} 
                        type="password" 
                        placeholder="••••••••" 
                        class="w-full bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-[22px] px-6 py-4 text-sm font-bold focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/30 transition-all outline-none text-slate-900 dark:text-slate-100" 
                    />
                </div>

                <div class="space-y-2">
                    <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">New Password</label>
                    <input 
                        bind:value={newPassword} 
                        type="password" 
                        placeholder="••••••••" 
                        class="w-full bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-[22px] px-6 py-4 text-sm font-bold focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/30 transition-all outline-none text-slate-900 dark:text-slate-100" 
                    />
                </div>

                <div class="space-y-2">
                    <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">Confirm New Password</label>
                    <input 
                        bind:value={confirmPassword} 
                        type="password" 
                        placeholder="••••••••" 
                        class="w-full bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-[22px] px-6 py-4 text-sm font-bold focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/30 transition-all outline-none text-slate-900 dark:text-slate-100" 
                    />
                </div>

                <div class="flex items-center space-x-3 pt-2">
                    <button 
                        onclick={() => showPasswordModal = false}
                        class="flex-1 px-6 py-4 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold rounded-[22px] hover:bg-slate-200 transition-all active:scale-95"
                    >
                        Cancel
                    </button>
                    <button 
                        onclick={handleUpdatePassword}
                        disabled={updating || !oldPassword || !newPassword || !confirmPassword}
                        class="flex-[2] px-6 py-4 bg-indigo-600 text-white font-bold rounded-[22px] hover:bg-indigo-700 transition-all active:scale-95 shadow-lg shadow-indigo-100 dark:shadow-none disabled:opacity-50"
                    >
                        {updating ? 'Updating...' : 'Update Password'}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

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
