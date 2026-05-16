<script lang="ts">
    import { X, Link, Mail, Trash2, Shield, UserPlus, Check, ChevronDown, ExternalLink } from 'lucide-svelte';
    import api, { BASE_URL } from '$lib/api';
    import { cn } from '$lib/utils';
    import { fade, fly, scale, slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { toasts } from '$lib/toasts';

    interface Permission {
        id: string;
        user_email: string;
        level: 'viewer' | 'editor';
    }

    interface Item {
        id: string;
        name: string;
        is_public: boolean;
        sharing_token?: string;
    }

    let { item, onclose } = $props<{
        item: Item;
        onclose: () => void;
    }>();

    let loading = $state(false);
    let publicEnabled = $state(item.is_public);
    let inviteEmail = $state('');
    let inviteLevel = $state<'viewer' | 'editor'>('viewer');
    let permissions = $state<Permission[]>([]);
    let showLevelDropdown = $state(false);

    async function fetchPermissions() {
        try {
            const response = await api.get(`/items/${item.id}/permissions`);
            permissions = response.data;
        } catch (e) {
            toasts.error('Failed to load permissions.');
        }
    }

    async function togglePublic() {
        loading = true;
        try {
            const response = await api.post(`/items/${item.id}/share`);
            item.is_public = response.data.is_public;
            item.sharing_token = response.data.sharing_token;
            publicEnabled = item.is_public;
            toasts.success(publicEnabled ? 'Public sharing enabled' : 'Public sharing disabled');
        } catch (e) {
            toasts.error('Failed to update public status.');
        } finally {
            loading = false;
        }
    }

    async function addPermission() {
        if (!inviteEmail) return;
        loading = true;
        try {
            const response = await api.post(`/items/${item.id}/permissions`, {
                user_email: inviteEmail,
                level: inviteLevel
            });
            permissions = [...permissions, response.data];
            inviteEmail = '';
            toasts.success(`Shared with ${inviteEmail}`);
        } catch (e: any) {
            toasts.error(e.response?.data?.detail || 'Failed to share file.');
        } finally {
            loading = false;
        }
    }

    async function removePermission(permId: string) {
        try {
            await api.delete(`/items/${item.id}/permissions/${permId}`);
            permissions = permissions.filter(p => p.id !== permId);
            toasts.info('Access revoked.');
        } catch (e) {
            toasts.error('Failed to remove access.');
        }
    }

    function copyLink() {
        if (!item.sharing_token) return;
        const shareUrl = `${window.location.origin}/share/${item.sharing_token}`;
        navigator.clipboard.writeText(shareUrl);
        toasts.success('Link copied to clipboard!');
    }

    $effect(() => {
        fetchPermissions();
    });
</script>

<div 
    class="fixed inset-0 bg-slate-900/60 dark:bg-[#020617]/80 backdrop-blur-md flex items-center justify-center z-[70] p-6"
    transition:fade={{ duration: 200 }}
>
    <div 
        class="bg-white dark:bg-slate-900 rounded-[40px] p-8 w-full max-w-lg shadow-2xl border border-white/20 dark:border-slate-800 relative overflow-hidden"
        transition:fly={{ y: 40, duration: 400, easing: quintOut }}
    >
        <div class="flex items-center justify-between mb-8">
            <div class="flex items-center space-x-4">
                <div class="bg-indigo-100 dark:bg-indigo-900/40 p-2.5 rounded-2xl">
                    <UserPlus class="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div>
                    <h2 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">Share "{item.name}"</h2>
                    <p class="text-slate-400 text-xs font-bold uppercase tracking-widest">Manage access & permissions</p>
                </div>
            </div>
            <button onclick={onclose} class="p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-slate-400 transition-all">
                <X class="w-5 h-5" />
            </button>
        </div>

        <div class="space-y-6">
            <!-- Invite Section -->
            <div class="space-y-3">
                <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Add People</label>
                <div class="flex space-x-2">
                    <div class="relative flex-1 group">
                        <Mail class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                        <input 
                            bind:value={inviteEmail} 
                            type="email" 
                            placeholder="user@example.com" 
                            class="w-full bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-2xl pl-12 pr-4 py-3 text-sm font-bold focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/30 transition-all outline-none text-slate-700 dark:text-slate-200" 
                        />
                    </div>
                    <div class="relative">
                        <button 
                            onclick={() => showLevelDropdown = !showLevelDropdown}
                            class="bg-slate-50 dark:bg-slate-800/50 px-4 py-3 rounded-2xl text-sm font-bold flex items-center space-x-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 transition-colors"
                        >
                            <span class="capitalize">{inviteLevel}</span>
                            <ChevronDown class="w-4 h-4" />
                        </button>
                        {#if showLevelDropdown}
                            <div 
                                class="absolute right-0 top-full mt-2 bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-100 dark:border-slate-700 p-2 z-50 min-w-[120px]"
                                in:scale={{ duration: 150, start: 0.95 }}
                            >
                                <button onclick={() => { inviteLevel = 'viewer'; showLevelDropdown = false; }} class="w-full text-left px-3 py-2 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">Viewer</button>
                                <button onclick={() => { inviteLevel = 'editor'; showLevelDropdown = false; }} class="w-full text-left px-3 py-2 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">Editor</button>
                            </div>
                        {/if}
                    </div>
                    <button 
                        onclick={addPermission} 
                        disabled={!inviteEmail || loading}
                        class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-6 rounded-2xl text-sm font-black transition-all active:scale-95 shadow-lg shadow-indigo-200 dark:shadow-none"
                    >
                        SEND
                    </button>
                </div>
            </div>

            <!-- Permissions List -->
            <div class="space-y-3">
                <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">People with access</label>
                <div class="max-h-40 overflow-y-auto custom-scrollbar space-y-2 pr-2">
                    <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-transparent">
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-[10px] font-black uppercase tracking-widest text-slate-500">ME</div>
                            <div class="flex flex-col">
                                <span class="text-xs font-bold text-slate-700 dark:text-slate-200">Owner</span>
                                <span class="text-[10px] text-slate-400 font-medium tracking-tight">Full access</span>
                            </div>
                        </div>
                    </div>
                    {#each permissions as perm}
                        <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-transparent hover:border-slate-100 dark:hover:border-slate-700 transition-all group" in:slide>
                            <div class="flex items-center space-x-3">
                                <div class="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-[10px] font-black uppercase text-indigo-600">{perm.user_email[0]}</div>
                                <div class="flex flex-col">
                                    <span class="text-xs font-bold text-slate-700 dark:text-slate-200 truncate max-w-[180px]">{perm.user_email}</span>
                                    <span class="text-[10px] text-slate-400 font-medium capitalize tracking-tight">{perm.level}</span>
                                </div>
                            </div>
                            <button onclick={() => removePermission(perm.id)} class="p-2 text-slate-300 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-xl transition-all opacity-0 group-hover:opacity-100">
                                <Trash2 class="w-4 h-4" />
                            </button>
                        </div>
                    {/each}
                </div>
            </div>

            <div class="h-px bg-slate-100 dark:bg-slate-800"></div>

            <!-- General Access Section -->
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class={cn("p-2 rounded-xl transition-colors", publicEnabled ? "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600" : "bg-slate-100 dark:bg-slate-800 text-slate-400")}>
                            {#if publicEnabled}
                                <ExternalLink class="w-4 h-4" />
                            {:else}
                                <Shield class="w-4 h-4" />
                            {/if}
                        </div>
                        <div>
                            <span class="text-xs font-bold text-slate-700 dark:text-slate-200">General Access</span>
                            <p class="text-[10px] text-slate-400 font-medium tracking-tight">
                                {publicEnabled ? 'Anyone with the link can view' : 'Restricted to invited people'}
                            </p>
                        </div>
                    </div>
                    <button 
                        onclick={togglePublic} 
                        class={cn(
                            "px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all",
                            publicEnabled ? "bg-rose-50 dark:bg-rose-900/20 text-rose-600 hover:bg-rose-100" : "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 hover:bg-emerald-100"
                        )}
                    >
                        {publicEnabled ? 'Disable Link' : 'Enable Link'}
                    </button>
                </div>

                {#if publicEnabled}
                    <div class="flex space-x-2" in:slide>
                        <div class="flex-1 bg-slate-50 dark:bg-slate-800/50 px-4 py-3 rounded-2xl border-2 border-slate-100 dark:border-slate-800 flex items-center overflow-hidden">
                            <Link class="w-4 h-4 text-slate-400 shrink-0 mr-3" />
                            <span class="text-[10px] font-bold text-slate-500 truncate select-all">{window.location.origin}/share/{item.sharing_token}</span>
                        </div>
                        <button 
                            onclick={copyLink}
                            class="bg-white dark:bg-slate-800 border-2 border-slate-100 dark:border-slate-700 px-4 rounded-2xl text-[10px] font-black uppercase tracking-widest text-indigo-600 dark:text-indigo-400 hover:bg-slate-50 transition-all active:scale-95"
                        >
                            Copy
                        </button>
                    </div>
                {/if}
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
