<script lang="ts">
    import { onMount } from 'svelte';
    import api from '$lib/api';
    import { 
        Folder, 
        Star, 
        Download, 
        Trash,
        File as FileIcon,
        Plus,
        Upload,
        MoreHorizontal,
        Share2,
        Info,
        ChevronRight,
        Search,
        LayoutGrid,
        LayoutList,
        FolderPlus,
        UploadCloud,
        X
    } from 'lucide-svelte';
    import { cn } from '$lib/utils';
    import { fade, fly, scale, slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    interface Item {
        id: string;
        name: string;
        is_folder: boolean;
        size?: number;
        mime_type?: string;
        is_starred: boolean;
        is_trashed: boolean;
        updated_at: string;
    }

    let { 
        title = "My Drive", 
        isStarred = undefined, 
        isTrashed = false, 
        isRecent = false 
    } = $props<{
        title?: string;
        isStarred?: boolean;
        isTrashed?: boolean;
        isRecent?: boolean;
    }>();

    let items = $state<Item[]>([]);
    let loading = $state(true);
    let viewMode = $state<'list' | 'grid'>('list');
    let searchQuery = $state('');
    let currentFolderId = $state<string | null>(null);
    let showUploadModal = $state(false);
    let newFolderName = $state('');
    let fileToUpload = $state<File | null>(null);
    let selectedItemId = $state<string | null>(null);

    async function fetchItems() {
        loading = true;
        try {
            const params = {
                parent_id: currentFolderId,
                search: searchQuery || undefined,
                is_starred: isStarred,
                is_trashed: isTrashed
            };
            const response = await api.get('/items/', { params });
            items = response.data;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(fetchItems);

    export function handleSearch(query: string) {
        searchQuery = query;
        fetchItems();
    }

    function formatSize(bytes?: number) {
        if (!bytes) return '-';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async function toggleStar(item: Item) {
        try {
            await api.patch(`/items/${item.id}/`, { is_starred: !item.is_starred });
            fetchItems();
        } catch (e) {
            console.error(e);
        }
    }

    async function moveToTrash(item: Item) {
        try {
            await api.delete(`/items/${item.id}/`);
            fetchItems();
        } catch (e) {
            console.error(e);
        }
    }

    function downloadFile(item: Item) {
        window.open(`http://localhost:8000/api/v1/items/${item.id}/download/`, '_blank');
    }

    function openFolder(folder: Item) {
        currentFolderId = folder.id;
        fetchItems();
    }

    async function createFolder() {
        if (!newFolderName) return;
        try {
            await api.post('/items/folders/', { name: newFolderName, parent_id: currentFolderId });
            newFolderName = '';
            showUploadModal = false;
            fetchItems();
        } catch (e) {
            console.error(e);
        }
    }

    async function uploadFile() {
        if (!fileToUpload) return;
        try {
            const formData = new FormData();
            formData.append('file', fileToUpload);
            if (currentFolderId) formData.append('parent_id', currentFolderId);
            
            await api.post('/items/upload/', formData);
            fileToUpload = null;
            showUploadModal = false;
            fetchItems();
        } catch (e) {
            console.error(e);
        }
    }

    function handleFileChange(e: Event) {
        const target = e.target as HTMLInputElement;
        if (target.files) {
            fileToUpload = target.files[0];
        }
    }

    function goBack() {
        currentFolderId = null;
        fetchItems();
    }
</script>

<div class="flex-1 flex flex-col bg-slate-50/50 overflow-hidden relative">
    <!-- Sub Header / Breadcrumbs -->
    <div class="flex items-center justify-between px-8 py-6">
        <div class="flex items-center space-x-2 text-sm font-medium">
            <button onclick={goBack} class="text-slate-400 hover:text-indigo-600 transition-colors">SkyVault</button>
            <ChevronRight class="w-4 h-4 text-slate-300" />
            <span class="text-slate-900 font-bold text-lg">{title}</span>
        </div>

        <div class="flex items-center space-x-3">
            <div class="flex bg-white p-1 rounded-xl border border-slate-100 shadow-sm">
                <button 
                    onclick={() => viewMode = 'list'}
                    class={cn("p-1.5 rounded-lg transition-all", viewMode === 'list' ? "bg-indigo-50 text-indigo-600" : "text-slate-400 hover:text-slate-600")}
                >
                    <LayoutList class="w-4 h-4" />
                </button>
                <button 
                    onclick={() => viewMode = 'grid'}
                    class={cn("p-1.5 rounded-lg transition-all", viewMode === 'grid' ? "bg-indigo-50 text-indigo-600" : "text-slate-400 hover:text-slate-600")}
                >
                    <LayoutGrid class="w-4 h-4" />
                </button>
            </div>
            
            <button 
                onclick={() => showUploadModal = true}
                class="flex items-center space-x-2 bg-indigo-600 text-white rounded-xl px-4 py-2 shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all font-bold text-sm"
            >
                <Plus class="w-4 h-4" />
                <span>Create</span>
            </button>
        </div>
    </div>

    <main class="flex-1 overflow-y-auto px-8 pb-8">
        {#if loading}
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {#each Array(8) as _}
                    <div class="animate-pulse bg-white/60 h-32 rounded-2xl border border-slate-100"></div>
                {/each}
            </div>
        {:else if items.length === 0}
            <div class="flex flex-col items-center justify-center h-[60vh] text-center" in:fade>
                <div class="bg-indigo-50 p-6 rounded-full mb-6">
                    <UploadCloud class="w-16 h-16 text-indigo-200" />
                </div>
                <h3 class="text-xl font-bold text-slate-800 mb-2">Your vault is empty</h3>
                <p class="text-slate-500 max-w-xs mx-auto">Upload your first file or create a folder to start organizing your digital life.</p>
                <button 
                    onclick={() => showUploadModal = true}
                    class="mt-8 text-indigo-600 font-bold hover:bg-indigo-50 px-6 py-2 rounded-xl transition-colors"
                >
                    Get Started
                </button>
            </div>
        {:else if viewMode === 'list'}
            <div class="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden" in:fly={{ y: 20, duration: 400 }}>
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="text-[11px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-50 bg-slate-50/30">
                            <th class="py-4 px-6">File Name</th>
                            <th class="py-4 px-6">Date Modified</th>
                            <th class="py-4 px-6">Size</th>
                            <th class="py-4 px-6 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-50">
                        {#each items as item (item.id)}
                            <tr 
                                class={cn(
                                    "group hover:bg-slate-50/80 transition-colors cursor-pointer",
                                    selectedItemId === item.id && "bg-indigo-50/30"
                                )}
                                onclick={() => selectedItemId = item.id}
                                in:fade
                            >
                                <td class="py-4 px-6">
                                    <div class="flex items-center space-x-4">
                                        <div class={cn(
                                            "p-2.5 rounded-xl transition-colors",
                                            item.is_folder ? "bg-amber-50 text-amber-500" : "bg-indigo-50 text-indigo-500"
                                        )}>
                                            {#if item.is_folder}
                                                <Folder class="w-5 h-5 fill-current" />
                                            {:else}
                                                <FileIcon class="w-5 h-5" />
                                            {/if}
                                        </div>
                                        <div>
                                            {#if item.is_folder}
                                                <button onclick={(e) => { e.stopPropagation(); openFolder(item); }} class="font-bold text-slate-800 hover:text-indigo-600 transition-colors">{item.name}</button>
                                            {:else}
                                                <span class="font-bold text-slate-800">{item.name}</span>
                                            {/if}
                                            <div class="text-[10px] text-slate-400 font-medium uppercase tracking-tighter mt-0.5">
                                                {item.mime_type || (item.is_folder ? 'Folder' : 'Unknown')}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td class="py-4 px-6">
                                    <span class="text-sm font-semibold text-slate-500">{new Date(item.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                                </td>
                                <td class="py-4 px-6">
                                    <span class="text-sm font-semibold text-slate-500">{formatSize(item.size)}</span>
                                </td>
                                <td class="py-4 px-6 text-right">
                                    <div class="flex items-center justify-end space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button onclick={(e) => { e.stopPropagation(); toggleStar(item); }} class={cn("p-2 rounded-lg hover:bg-white transition-colors shadow-sm border border-transparent hover:border-slate-100", item.is_starred ? "text-amber-500" : "text-slate-400")}>
                                            <Star class={cn("w-4 h-4", item.is_starred && "fill-current")} />
                                        </button>
                                        {#if !item.is_folder}
                                            <button onclick={(e) => { e.stopPropagation(); downloadFile(item); }} class="p-2 rounded-lg hover:bg-white transition-colors shadow-sm border border-transparent hover:border-slate-100 text-slate-400 hover:text-indigo-600">
                                                <Download class="w-4 h-4" />
                                            </button>
                                        {/if}
                                        <button onclick={(e) => { e.stopPropagation(); moveToTrash(item); }} class="p-2 rounded-lg hover:bg-white transition-colors shadow-sm border border-transparent hover:border-slate-100 text-slate-400 hover:text-rose-500">
                                            <Trash class="w-4 h-4" />
                                        </button>
                                        <button class="p-2 rounded-lg hover:bg-white transition-colors shadow-sm border border-transparent hover:border-slate-100 text-slate-400">
                                            <MoreHorizontal class="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {:else}
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6" in:fly={{ y: 20, duration: 400 }}>
                {#each items as item (item.id)}
                    <div 
                        class={cn(
                            "bg-white p-5 rounded-3xl border border-slate-100 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 transition-all group relative cursor-pointer",
                            selectedItemId === item.id && "ring-2 ring-indigo-500 border-transparent shadow-indigo-100 shadow-lg"
                        )}
                        onclick={() => selectedItemId = item.id}
                        in:scale={{ duration: 300, start: 0.95 }}
                    >
                        <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onclick={(e) => { e.stopPropagation(); toggleStar(item); }} class={cn("p-1.5 rounded-lg bg-white/80 backdrop-blur shadow-sm", item.is_starred ? "text-amber-500" : "text-slate-400")}>
                                <Star class={cn("w-3 h-3", item.is_starred && "fill-current")} />
                            </button>
                        </div>

                        <div class="flex flex-col items-center text-center">
                            <div class={cn(
                                "w-16 h-16 flex items-center justify-center rounded-2xl mb-4 transition-transform group-hover:scale-110 duration-300",
                                item.is_folder ? "bg-amber-50 text-amber-500" : "bg-indigo-50 text-indigo-500"
                            )}>
                                {#if item.is_folder}
                                    <Folder class="w-8 h-8 fill-current" />
                                {:else}
                                    <FileIcon class="w-8 h-8" />
                                {/if}
                            </div>
                            <div class="w-full">
                                <h4 class="font-bold text-slate-800 text-sm truncate px-2">{item.name}</h4>
                                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">{item.is_folder ? 'Folder' : formatSize(item.size)}</p>
                            </div>
                        </div>

                        {#if item.is_folder}
                            <button 
                                onclick={(e) => { e.stopPropagation(); openFolder(item); }}
                                class="absolute inset-0 z-0"
                            ></button>
                        {/if}
                    </div>
                {/each}
            </div>
        {/if}
    </main>
</div>

{#if showUploadModal}
    <div 
        class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="bg-white rounded-[32px] p-8 w-full max-w-md shadow-2xl border border-slate-100 relative overflow-hidden"
            transition:fly={{ y: 20, duration: 300, easing: quintOut }}
        >
            <div class="absolute top-0 right-0 p-6">
                <button onclick={() => showUploadModal = false} class="p-2 hover:bg-slate-50 rounded-full text-slate-400 transition-colors">
                    <X class="w-5 h-5" />
                </button>
            </div>

            <h2 class="text-2xl font-bold text-slate-800 mb-8 flex items-center space-x-3">
                <div class="bg-indigo-600 p-2 rounded-xl">
                    <Plus class="w-5 h-5 text-white" />
                </div>
                <span>New Resource</span>
            </h2>
            
            <div class="space-y-8">
                <div>
                    <label for="folder-name" class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Create Folder</label>
                    <div class="flex space-x-2">
                        <div class="relative flex-1">
                            <FolderPlus class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                            <input 
                                id="folder-name" 
                                bind:value={newFolderName} 
                                type="text" 
                                placeholder="Name your folder..." 
                                class="w-full bg-slate-50 border-2 border-transparent rounded-2xl pl-12 pr-4 py-3 text-sm font-semibold focus:bg-white focus:border-indigo-100 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" 
                            />
                        </div>
                        <button onclick={createFolder} class="bg-indigo-600 text-white px-6 rounded-2xl text-sm font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all">Create</button>
                    </div>
                </div>
                
                <div class="relative">
                    <div class="absolute inset-0 flex items-center" aria-hidden="true">
                        <div class="w-full border-t border-slate-100"></div>
                    </div>
                    <div class="relative flex justify-center text-sm">
                        <span class="px-4 bg-white text-xs font-bold text-slate-300 uppercase tracking-widest">or</span>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Upload Assets</label>
                    <div class="group relative bg-slate-50 border-2 border-dashed border-slate-200 rounded-[24px] p-8 transition-all hover:bg-indigo-50/50 hover:border-indigo-200">
                        <input 
                            id="file-upload" 
                            type="file" 
                            onchange={handleFileChange} 
                            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
                        />
                        <div class="text-center">
                            <div class="bg-white w-12 h-12 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                                <UploadCloud class="w-6 h-6 text-indigo-500" />
                            </div>
                            <p class="text-sm font-bold text-slate-700 mb-1">
                                {fileToUpload ? fileToUpload.name : 'Choose a file'}
                            </p>
                            <p class="text-xs font-medium text-slate-400">Drag & drop or click to browse</p>
                        </div>
                    </div>
                    
                    {#if fileToUpload}
                        <button 
                            onclick={uploadFile} 
                            class="w-full mt-4 bg-indigo-600 text-white py-4 rounded-2xl text-sm font-bold shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-all"
                            in:slide
                        >
                            Upload to SkyVault
                        </button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    @reference "tailwindcss";

    :global(body) {
        @apply bg-slate-50;
    }

    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        @apply bg-transparent;
    }

    ::-webkit-scrollbar-thumb {
        @apply bg-slate-200 rounded-full hover:bg-slate-300 transition-colors;
    }
</style>
