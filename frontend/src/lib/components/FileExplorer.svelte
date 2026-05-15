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
        Upload
    } from 'lucide-svelte';

    export let title = "My Drive";
    export let isStarred = undefined;
    export let isTrashed = false;
    export let isRecent = false;

    let items = [];
    let loading = true;
    let viewMode = 'list';
    let searchQuery = '';
    let currentFolderId = null;
    let showUploadModal = false;
    let newFolderName = '';
    let fileToUpload = null;

    async function fetchItems() {
        loading = true;
        try {
            const params = {
                parent_id: currentFolderId,
                search: searchQuery || undefined,
                is_starred: isStarred,
                is_trashed: isTrashed
            };
            const response = await api.get('/items', { params });
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

    function formatSize(bytes: number) {
        if (!bytes) return '-';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async function toggleStar(item) {
        try {
            await api.patch(`/items/${item.id}`, { is_starred: !item.is_starred });
            fetchItems();
        } catch (e) {
            console.error(e);
        }
    }

    async function moveToTrash(item) {
        try {
            await api.delete(`/items/${item.id}`);
            fetchItems();
        } catch (e) {
            console.error(e);
        }
    }

    function downloadFile(item) {
        window.open(`http://localhost:8000/api/v1/items/${item.id}/download`, '_blank');
    }

    function openFolder(folder) {
        currentFolderId = folder.id;
        fetchItems();
    }

    async function createFolder() {
        if (!newFolderName) return;
        try {
            await api.post('/folders', { name: newFolderName, parent_id: currentFolderId });
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
            
            await api.post('/upload', formData);
            fileToUpload = null;
            showUploadModal = false;
            fetchItems();
        } catch (e) {
            console.error(e);
        }
    }
</script>

<div class="flex-1 flex flex-col overflow-hidden">
    <div class="flex items-center justify-between mb-6 p-6">
        <h1 class="text-2xl font-semibold text-gray-800">{title}</h1>
        <button 
            on:click={() => showUploadModal = true}
            class="flex items-center space-x-2 bg-blue-600 text-white rounded-full px-6 py-2 shadow-sm hover:bg-blue-700 transition-colors"
        >
            <Plus class="w-5 h-5" />
            <span class="font-medium">New</span>
        </button>
    </div>

    <main class="flex-1 overflow-y-auto px-6 bg-white">
        {#if loading}
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {#each Array(8) as _}
                    <div class="animate-pulse bg-gray-100 h-24 rounded-lg"></div>
                {/each}
            </div>
        {:else if items.length === 0}
            <div class="flex flex-col items-center justify-center h-64 text-gray-400">
                <Folder class="w-16 h-16 mb-4 opacity-20" />
                <p>No files or folders here</p>
            </div>
        {:else}
            <div class="min-w-full">
                <table class="min-w-full">
                    <thead>
                        <tr class="text-left text-sm font-medium text-gray-500 border-b border-gray-200">
                            <th class="pb-3 px-4">Name</th>
                            <th class="pb-3 px-4">Owner</th>
                            <th class="pb-3 px-4">Last modified</th>
                            <th class="pb-3 px-4">File size</th>
                            <th class="pb-3 px-4"></th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        {#each items as item}
                            <tr class="hover:bg-gray-50 group">
                                <td class="py-3 px-4">
                                    <div class="flex items-center space-x-3">
                                        {#if item.is_folder}
                                            <Folder class="w-5 h-5 text-gray-400" />
                                            <button on:click={() => openFolder(item)} class="text-sm font-medium text-gray-700 hover:underline">{item.name}</button>
                                        {:else}
                                            <FileIcon class="w-5 h-5 text-blue-500" />
                                            <span class="text-sm text-gray-700">{item.name}</span>
                                        {/if}
                                    </div>
                                </td>
                                <td class="py-3 px-4 text-sm text-gray-500">me</td>
                                <td class="py-3 px-4 text-sm text-gray-500">{new Date(item.updated_at).toLocaleDateString()}</td>
                                <td class="py-3 px-4 text-sm text-gray-500">{formatSize(item.size)}</td>
                                <td class="py-3 px-4">
                                    <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button on:click={() => toggleStar(item)} class="p-1 hover:bg-gray-200 rounded {item.is_starred ? 'text-yellow-500' : 'text-gray-400'}">
                                            <Star class="w-4 h-4 fill-current" />
                                        </button>
                                        {#if !item.is_folder}
                                            <button on:click={() => downloadFile(item)} class="p-1 hover:bg-gray-200 rounded text-gray-400">
                                                <Download class="w-4 h-4" />
                                            </button>
                                        {/if}
                                        <button on:click={() => moveToTrash(item)} class="p-1 hover:bg-gray-200 rounded text-gray-400">
                                            <Trash class="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </main>
</div>

{#if showUploadModal}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-96 shadow-xl">
            <h2 class="text-xl font-semibold mb-4 text-gray-800">New Item</h2>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Create Folder</label>
                    <div class="flex space-x-2">
                        <input bind:value={newFolderName} type="text" placeholder="Folder name" class="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500" />
                        <button on:click={createFolder} class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium">Create</button>
                    </div>
                </div>
                
                <div class="border-t pt-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Upload File</label>
                    <div class="flex flex-col space-y-2">
                        <input type="file" on:change={(e) => fileToUpload = e.target.files[0]} class="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
                        <button on:click={uploadFile} disabled={!fileToUpload} class="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium disabled:opacity-50">Upload</button>
                    </div>
                </div>
            </div>
            
            <div class="mt-6 flex justify-end">
                <button on:click={() => showUploadModal = false} class="text-gray-500 hover:text-gray-700 font-medium text-sm">Cancel</button>
            </div>
        </div>
    </div>
{/if}
