<script lang="ts">
    import { onMount } from 'svelte';
    import api, { BASE_URL } from '$lib/api';
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
        X,
        History,
        ArrowLeft,
        ExternalLink,
        FileText,
        Image as ImageIcon,
        Music,
        Video,
        FileCode
    } from 'lucide-svelte';
    import { cn } from '$lib/utils';
    import { fade, fly, scale, slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { toasts } from '$lib/toasts';

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
        title = "My Assets", 
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
    let viewMode = $state<'list' | 'grid'>('grid');
    let searchQuery = $state('');
    let currentFolderId = $state<string | null>(null);
    let breadcrumbs = $state<{id: string | null, name: string}[]>([{id: null, name: 'Root'}]);
    
    let showUploadModal = $state(false);
    let newFolderName = $state('');
    let fileToUpload = $state<File | null>(null);
    let selectedItemId = $state<string | null>(null);
    let isDragging = $state(false);

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
            toasts.error('Failed to sync with drive.');
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
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function getFileIcon(item: Item) {
        if (item.is_folder) return Folder;
        const mime = item.mime_type?.toLowerCase() || '';
        if (mime.includes('image')) return ImageIcon;
        if (mime.includes('video')) return Video;
        if (mime.includes('audio')) return Music;
        if (mime.includes('text') || mime.includes('pdf')) return FileText;
        if (mime.includes('javascript') || mime.includes('json') || mime.includes('html')) return FileCode;
        return FileIcon;
    }

    async function toggleStar(item: Item) {
        try {
            await api.patch(`/items/${item.id}/`, { is_starred: !item.is_starred });
            items = items.map(i => i.id === item.id ? { ...i, is_starred: !i.is_starred } : i);
            toasts.success(item.is_starred ? 'Removed from favorites' : 'Added to favorites');
        } catch (e) {
            toasts.error('Failed to update favorite status.');
        }
    }

    async function moveToTrash(item: Item) {
        try {
            await api.delete(`/items/${item.id}/`);
            items = items.filter(i => i.id !== item.id);
            toasts.success(isTrashed ? 'Permanently deleted' : 'Moved to trash');
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    function downloadFile(item: Item) {
        window.open(`${BASE_URL}/items/${item.id}/download/`, '_blank');
        toasts.info(`Downloading ${item.name}...`);
    }

    function openFolder(folder: Item) {
        currentFolderId = folder.id;
        breadcrumbs = [...breadcrumbs, { id: folder.id, name: folder.name }];
        fetchItems();
    }

    function navigateToBreadcrumb(crumb: {id: string | null, name: string}, index: number) {
        currentFolderId = crumb.id;
        breadcrumbs = breadcrumbs.slice(0, index + 1);
        fetchItems();
    }

    async function createFolder() {
        if (!newFolderName) return;
        try {
            await api.post('/items/folders/', { name: newFolderName, parent_id: currentFolderId });
            newFolderName = '';
            showUploadModal = false;
            fetchItems();
            toasts.success('Folder created successfully.');
        } catch (e) {
            toasts.error('Failed to create folder.');
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
            toasts.success('Asset uploaded to drive.');
        } catch (e) {
            toasts.error('Upload failed.');
        }
    }

    function handleFileChange(e: Event) {
        const target = e.target as HTMLInputElement;
        if (target.files) {
            fileToUpload = target.files[0];
        }
    }

    function handleDrop(e: DragEvent) {
        e.preventDefault();
        isDragging = false;
        if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
            fileToUpload = e.dataTransfer.files[0];
            showUploadModal = true;
        }
    }
</script>

<div 
    class="flex-1 flex flex-col bg-slate-50 dark:bg-[#0f172a] overflow-hidden relative transition-colors duration-300"
    ondragover={(e) => { e.preventDefault(); isDragging = true; }}
    ondragleave={() => isDragging = false}
    ondrop={handleDrop}
>
    <!-- Drag & Drop Overlay -->
    {#if isDragging}
        <div 
            class="absolute inset-0 z-50 bg-indigo-600/10 dark:bg-indigo-600/20 backdrop-blur-sm flex items-center justify-center p-12"
            transition:fade
        >
            <div class="w-full h-full border-4 border-dashed border-indigo-600 dark:border-indigo-400 rounded-[40px] flex flex-col items-center justify-center text-indigo-600 dark:text-indigo-400 animate-pulse">
                <UploadCloud class="w-24 h-24 mb-6" />
                <h2 class="text-4xl font-black tracking-tighter">Drop to Upload to DRIVE X</h2>
            </div>
        </div>
    {/if}

    <!-- Toolbar / Breadcrumbs -->
    <div class="flex flex-col md:flex-row md:items-center justify-between px-8 py-8 gap-4">
        <div>
            <div class="flex items-center space-x-2 text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-3">
                <History class="w-3 h-3" />
                <span>Path Explorer</span>
            </div>
            <div class="flex items-center space-x-1 overflow-x-auto no-scrollbar">
                {#each breadcrumbs as crumb, i}
                    <button 
                        onclick={() => navigateToBreadcrumb(crumb, i)}
                        class={cn(
                            "flex items-center px-3 py-1.5 rounded-xl transition-all whitespace-nowrap font-bold text-sm",
                            i === breadcrumbs.length - 1 
                                ? "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400" 
                                : "text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                        )}
                    >
                        {crumb.name}
                    </button>
                    {#if i < breadcrumbs.length - 1}
                        <ChevronRight class="w-4 h-4 text-slate-300 dark:text-slate-700 shrink-0" />
                    {/if}
                {/each}
            </div>
        </div>

        <div class="flex items-center space-x-4">
            <!-- View Mode Switcher -->
            <div class="flex bg-white dark:bg-slate-800 p-1.5 rounded-[18px] border border-slate-200/50 dark:border-slate-700/50 shadow-sm">
                <button 
                    onclick={() => viewMode = 'list'}
                    class={cn(
                        "p-2 rounded-xl transition-all flex items-center space-x-2 px-3", 
                        viewMode === 'list' 
                            ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 shadow-inner" 
                            : "text-slate-400 dark:text-slate-500 hover:text-slate-600"
                    )}
                >
                    <LayoutList class="w-4 h-4" />
                    <span class="text-xs font-black uppercase tracking-widest hidden lg:block">List</span>
                </button>
                <button 
                    onclick={() => viewMode = 'grid'}
                    class={cn(
                        "p-2 rounded-xl transition-all flex items-center space-x-2 px-3", 
                        viewMode === 'grid' 
                            ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 shadow-inner" 
                            : "text-slate-400 dark:text-slate-500 hover:text-slate-600"
                    )}
                >
                    <LayoutGrid class="w-4 h-4" />
                    <span class="text-xs font-black uppercase tracking-widest hidden lg:block">Grid</span>
                </button>
            </div>
            
            <button 
                id="create-btn"
                onclick={() => showUploadModal = true}
                class="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-[18px] px-6 py-3.5 shadow-xl shadow-indigo-200 dark:shadow-none transition-all active:scale-95 font-bold text-sm tracking-tight"
            >
                <Plus class="w-4 h-4 stroke-[3px]" />
                <span>New Asset</span>
            </button>
        </div>
    </div>

    <!-- Content Area -->
    <main class="flex-1 overflow-y-auto px-8 pb-12 custom-scrollbar">
        {#if loading}
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-6">
                {#each Array(12) as _}
                    <div class="bg-white/50 dark:bg-slate-800/30 h-48 rounded-[32px] border border-slate-100 dark:border-slate-800/50 animate-pulse flex flex-col p-6 space-y-4">
                        <div class="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded-2xl"></div>
                        <div class="h-4 bg-slate-200 dark:bg-slate-700 rounded-full w-3/4"></div>
                        <div class="h-3 bg-slate-100 dark:bg-slate-800 rounded-full w-1/2"></div>
                    </div>
                {/each}
            </div>
        {:else if items.length === 0}
            <div class="flex flex-col items-center justify-center h-[50vh] text-center" in:fade>
                <div class="relative mb-8">
                    <div class="bg-indigo-600/5 dark:bg-indigo-600/10 w-32 h-32 rounded-[40px] flex items-center justify-center animate-bounce duration-[3000ms]">
                        <UploadCloud class="w-16 h-16 text-indigo-200 dark:text-indigo-900" />
                    </div>
                    <div class="absolute -top-2 -right-2 bg-white dark:bg-slate-800 p-3 rounded-2xl shadow-xl border border-slate-50 dark:border-slate-700">
                        <Plus class="w-4 h-4 text-indigo-600" />
                    </div>
                </div>
                <h3 class="text-3xl font-black text-slate-900 dark:text-white tracking-tighter mb-3">Your Cloud Drive is Ready</h3>
                <p class="text-slate-500 dark:text-slate-400 max-w-sm mx-auto font-medium leading-relaxed">
                    Organize your assets, collaborate with your team, and access your data from anywhere in the universe.
                </p>
                <button 
                    onclick={() => showUploadModal = true}
                    class="mt-10 px-8 py-4 bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 font-black rounded-2xl border-2 border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all shadow-sm"
                >
                    Upload Your First Asset
                </button>
            </div>
        {:else if viewMode === 'list'}
            <div class="bg-white dark:bg-slate-900 rounded-[32px] border border-slate-200/50 dark:border-slate-800 shadow-sm overflow-hidden" in:fly={{ y: 20, duration: 400 }}>
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] border-b border-slate-50 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
                            <th class="py-5 px-8">Asset Name</th>
                            <th class="py-5 px-8 hidden md:table-cell">Modification Date</th>
                            <th class="py-5 px-8 hidden sm:table-cell">Metadata</th>
                            <th class="py-5 px-8 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-50 dark:divide-slate-800 transition-colors">
                        {#each items as item (item.id)}
                            {@const Icon = getFileIcon(item)}
                            <tr 
                                class={cn(
                                    "group hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-colors cursor-pointer",
                                    selectedItemId === item.id && "bg-indigo-50/50 dark:bg-indigo-900/20"
                                )}
                                onclick={() => selectedItemId = item.id}
                                in:fade
                            >
                                <td class="py-5 px-8">
                                    <div class="flex items-center space-x-5">
                                        <div class={cn(
                                            "p-3 rounded-2xl transition-all shadow-sm group-hover:scale-110",
                                            item.is_folder 
                                                ? "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400" 
                                                : "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400"
                                        )}>
                                            <Icon class={cn("w-5 h-5", item.is_folder && "fill-current")} />
                                        </div>
                                        <div class="flex flex-col min-w-0">
                                            {#if item.is_folder}
                                                <button onclick={(e) => { e.stopPropagation(); openFolder(item); }} class="font-black text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors text-sm truncate tracking-tight">{item.name}</button>
                                            {:else}
                                                <span class="font-black text-slate-900 dark:text-white text-sm truncate tracking-tight">{item.name}</span>
                                            {/if}
                                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1 truncate">
                                                {item.is_folder ? 'Folder Container' : item.mime_type || 'Unclassified Data'}
                                            </span>
                                        </div>
                                    </div>
                                </td>
                                <td class="py-5 px-8 hidden md:table-cell">
                                    <span class="text-xs font-bold text-slate-500 dark:text-slate-400">{new Date(item.updated_at).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}</span>
                                </td>
                                <td class="py-5 px-8 hidden sm:table-cell">
                                    <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded-lg uppercase">{item.is_folder ? 'CONTAINER' : formatSize(item.size)}</span>
                                </td>
                                <td class="py-5 px-8 text-right">
                                    <div class="flex items-center justify-end space-x-2 opacity-0 group-hover:opacity-100 transition-all translate-x-2 group-hover:translate-x-0">
                                        <button onclick={(e) => { e.stopPropagation(); toggleStar(item); }} class={cn("p-2.5 rounded-xl hover:bg-white dark:hover:bg-slate-800 transition-all shadow-sm border border-transparent hover:border-slate-100 dark:hover:border-slate-700", item.is_starred ? "text-amber-500" : "text-slate-400")}>
                                            <Star class={cn("w-4 h-4", item.is_starred && "fill-current")} />
                                        </button>
                                        {#if !item.is_folder}
                                            <button onclick={(e) => { e.stopPropagation(); downloadFile(item); }} class="p-2.5 rounded-xl hover:bg-white dark:hover:bg-slate-800 transition-all shadow-sm border border-transparent hover:border-slate-100 dark:hover:border-slate-700 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400">
                                                <Download class="w-4 h-4" />
                                            </button>
                                        {/if}
                                        <button onclick={(e) => { e.stopPropagation(); moveToTrash(item); }} class="p-2.5 rounded-xl hover:bg-white dark:hover:bg-slate-800 transition-all shadow-sm border border-transparent hover:border-slate-100 dark:hover:border-slate-700 text-slate-400 hover:text-rose-500">
                                            <Trash class="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {:else}
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-8" in:fly={{ y: 20, duration: 400 }}>
                {#each items as item (item.id)}
                    {@const Icon = getFileIcon(item)}
                    <div 
                        class={cn(
                            "group bg-white dark:bg-slate-800/40 p-6 rounded-[40px] border-2 border-transparent transition-all duration-500 relative cursor-pointer flex flex-col items-center text-center",
                            selectedItemId === item.id 
                                ? "border-indigo-500 bg-white dark:bg-slate-800 shadow-2xl shadow-indigo-500/10 scale-[1.02]" 
                                : "hover:bg-white dark:hover:bg-slate-800 hover:shadow-2xl hover:shadow-indigo-500/5 hover:-translate-y-1 border-slate-100 dark:border-slate-800/50 shadow-sm"
                        )}
                        onclick={() => selectedItemId = item.id}
                        in:scale={{ duration: 400, start: 0.9, easing: quintOut }}
                    >
                        <!-- Quick Actions Float -->
                        <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0 z-20 flex space-x-1">
                            <button onclick={(e) => { e.stopPropagation(); toggleStar(item); }} class={cn("p-2 rounded-xl bg-white/90 dark:bg-slate-800/90 backdrop-blur shadow-xl border border-slate-100 dark:border-slate-700", item.is_starred ? "text-amber-500" : "text-slate-400 hover:text-amber-500")}>
                                <Star class={cn("w-3.5 h-3.5", item.is_starred && "fill-current")} />
                            </button>
                            <button onclick={(e) => { e.stopPropagation(); moveToTrash(item); }} class="p-2 rounded-xl bg-white/90 dark:bg-slate-800/90 backdrop-blur shadow-xl border border-slate-100 dark:border-slate-700 text-slate-400 hover:text-rose-500">
                                <Trash class="w-3.5 h-3.5" />
                            </button>
                        </div>

                        <div class={cn(
                            "w-20 h-20 flex items-center justify-center rounded-[32px] mb-6 transition-all duration-500 group-hover:rotate-6 shadow-sm",
                            item.is_folder 
                                ? "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 group-hover:bg-amber-200" 
                                : "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 group-hover:bg-indigo-200"
                        )}>
                            <Icon class={cn("w-10 h-10 transition-transform duration-500", item.is_folder && "fill-current")} />
                        </div>
                        
                        <div class="w-full">
                            <h4 class="font-black text-slate-900 dark:text-white text-sm truncate px-1 tracking-tight mb-1">{item.name}</h4>
                            <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">{item.is_folder ? 'Container' : formatSize(item.size)}</p>
                        </div>

                        {#if item.is_folder}
                            <button 
                                onclick={(e) => { e.stopPropagation(); openFolder(item); }}
                                class="absolute inset-0 z-10"
                                aria-label="Open folder"
                            ></button>
                        {:else}
                            <button 
                                onclick={(e) => { e.stopPropagation(); downloadFile(item); }}
                                class="absolute inset-0 z-10"
                                aria-label="Download file"
                            ></button>
                        {/if}
                    </div>
                {/each}
            </div>
        {/if}
    </main>
</div>

<!-- Modern Upload Modal -->
{#if showUploadModal}
    <div 
        class="fixed inset-0 bg-slate-900/60 dark:bg-[#020617]/80 backdrop-blur-md flex items-center justify-center z-[60] p-6"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="bg-white dark:bg-slate-900 rounded-[48px] p-10 w-full max-w-xl shadow-2xl border border-white/20 dark:border-slate-800 relative overflow-hidden"
            transition:fly={{ y: 40, duration: 400, easing: quintOut }}
        >
            <div class="absolute top-0 right-0 p-8">
                <button onclick={() => { showUploadModal = false; fileToUpload = null; }} class="p-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-2xl text-slate-400 transition-all active:scale-90">
                    <X class="w-6 h-6" />
                </button>
            </div>

            <div class="flex items-center space-x-4 mb-12">
                <div class="bg-indigo-600 p-3.5 rounded-[24px] shadow-xl shadow-indigo-200 dark:shadow-none">
                    <Plus class="w-7 h-7 text-white stroke-[3px]" />
                </div>
                <div>
                    <h2 class="text-3xl font-black text-slate-900 dark:text-white tracking-tighter leading-none mb-1">Upload New Asset</h2>
                    <p class="text-slate-400 dark:text-slate-500 font-bold text-xs uppercase tracking-widest">Storage Management System</p>
                </div>
            </div>
            
            <div class="space-y-10">
                <!-- Create Folder Section -->
                <div>
                    <label for="folder-name" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-4">New Folder</label>
                    <div class="flex space-x-3">
                        <div class="relative flex-1 group">
                            <FolderPlus class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input 
                                id="folder-name" 
                                bind:value={newFolderName} 
                                type="text" 
                                placeholder="Identification label..." 
                                class="w-full bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-[24px] pl-14 pr-6 py-4 text-sm font-bold focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500/30 focus:ring-4 focus:ring-indigo-50 dark:focus:ring-indigo-900/10 transition-all outline-none text-slate-700 dark:text-slate-200" 
                            />
                        </div>
                        <button onclick={createFolder} class="bg-slate-900 dark:bg-indigo-600 hover:bg-black dark:hover:bg-indigo-700 text-white px-8 rounded-[24px] text-sm font-black transition-all active:scale-95 shadow-xl shadow-slate-200 dark:shadow-none">CREATE</button>
                    </div>
                </div>
                
                <div class="relative">
                    <div class="absolute inset-0 flex items-center" aria-hidden="true"><div class="w-full border-t border-slate-100 dark:border-slate-800"></div></div>
                    <div class="relative flex justify-center text-xs uppercase font-black text-slate-300 dark:text-slate-700"><span class="px-6 bg-white dark:bg-slate-900 transition-colors">OR UPLOAD FILE</span></div>
                </div>

                <!-- Upload Section -->
                <div>
                    <div 
                        class={cn(
                            "group relative bg-slate-50 dark:bg-slate-800/50 border-4 border-dashed rounded-[40px] p-12 transition-all duration-500",
                            fileToUpload 
                                ? "border-indigo-500 bg-indigo-50/30 dark:bg-indigo-900/20" 
                                : "border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-600 hover:bg-white dark:hover:bg-slate-800"
                        )}
                    >
                        <input 
                            id="file-upload" 
                            type="file" 
                            onchange={handleFileChange} 
                            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
                        />
                        <div class="text-center">
                            <div class={cn(
                                "w-20 h-20 rounded-[32px] shadow-sm flex items-center justify-center mx-auto mb-6 transition-all duration-500 group-hover:scale-110",
                                fileToUpload ? "bg-indigo-600 text-white rotate-0" : "bg-white dark:bg-slate-700 text-indigo-500 -rotate-6"
                            )}>
                                <UploadCloud class="w-10 h-10" />
                            </div>
                            <h3 class="text-lg font-black text-slate-900 dark:text-white mb-1 tracking-tight">
                                {fileToUpload ? fileToUpload.name : 'Upload Data to Drive'}
                            </h3>
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-tighter">
                                {fileToUpload ? `${formatSize(fileToUpload.size)} File` : 'Drag fragments or click to locate'}
                            </p>
                        </div>
                    </div>
                    
                    {#if fileToUpload}
                        <button 
                            onclick={uploadFile} 
                            class="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white py-5 rounded-[28px] text-lg font-black shadow-2xl shadow-indigo-200 dark:shadow-none transition-all active:scale-[0.98] flex items-center justify-center space-x-3"
                            in:slide
                        >
                            <span>UPLOAD ASSET</span>
                            <ArrowLeft class="w-6 h-6 rotate-180" />
                        </button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .no-scrollbar::-webkit-scrollbar {
        display: none;
    }
    .no-scrollbar {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
</style>
