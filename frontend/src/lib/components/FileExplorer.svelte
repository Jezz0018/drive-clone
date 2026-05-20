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
        MoreVertical,
        Share2,
        Info,
        ChevronRight,
        ChevronDown,
        Search,
        LayoutGrid,
        LayoutList,
        FolderPlus,
        UploadCloud,
        X,
        History,
        ArrowLeft,
        ArrowUp,
        ArrowDown,
        ArrowUpDown,
        Type,
        Calendar,
        HardDrive,
        ExternalLink,
        FileText,
        Image as ImageIcon,
        Music,
        Video,
        FileCode,
        Archive as ArchiveIcon
    } from 'lucide-svelte';
    import { cn } from '$lib/utils';
    import { fade, fly, scale, slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { user, storageUsage, ui } from '$lib/stores';
    import { toasts } from '$lib/toasts';
    import ShareModal from './ShareModal.svelte';
    import ContextMenu from './ContextMenu.svelte';
    import FilePreview from './FilePreview.svelte';

    interface Item {
        id: string;
        name: string;
        is_folder: boolean;
        size?: number;
        mime_type?: string;
        is_starred: boolean;
        is_trashed: boolean;
        is_archived: boolean;
        category?: string | null;
        category_id?: string | null;
        updated_at: string;
        is_public: boolean;
        sharing_token?: string;
        permissions?: any[];
    }

    let { 
        title = "My Files", 
        isStarred = undefined, 
        isTrashed = false, 
        isRecent = false,
        isArchived = false,
        category = undefined,
        sharedWithMe = false,
        mimeType = undefined
    } = $props<{
        title?: string;
        isStarred?: boolean;
        isTrashed?: boolean;
        isRecent?: boolean;
        isArchived?: boolean;
        category?: string;
        sharedWithMe?: boolean;
        mimeType?: string;
    }>();

    // UI State
    let items = $state<Item[]>([]);
    let loading = $state(true);
    let viewMode = $state<'list' | 'grid'>('grid');
    let searchQuery = $state('');
    let sortKey = $state<'name' | 'size' | 'date'>('name');
    let sortOrder = $state<'asc' | 'desc'>('asc');
    let showSortMenu = $state(false);
    
    // Core Logic State
    let currentFolderId = $state<string | null>(null);
    let breadcrumbs = $state<{id: string | null, name: string}[]>([{id: null, name: 'Root'}]);
    
    // Modal State
    let showUploadModal = $state(false);
    let newFolderName = $state('');
    let selectedCategory = $state<string | null>(null);
    let selectedCategoryId = $state<string | null>(null);
    let fileToUpload = $state<File | null>(null);

    // Interaction State
    let selectedItemIds = $state<Set<string>>(new Set());
    let isDragging = $state(false);
    let sharingItem = $state<Item | null>(null);
    let previewItem = $state<Item | null>(null);
    let customCategories = $state<any[]>([]);

    let showMoveModal = $state(false);
    let moveTargetItem = $state<Item | null>(null);
    let allFolders = $state<Item[]>([]);
    let selectedDestinationId = $state<string | null>(null);

    // Context Menu State
    let contextMenu = $state<{ x: number, y: number, item: Item } | null>(null);

    // Listen to Sidebar/Global Actions
    $effect(() => {
        if ($ui.showUploadModal) {
            showUploadModal = true;
            if ($ui.uploadType === 'folder') {
                newFolderName = 'New Folder';
                fileToUpload = null;
            } else {
                newFolderName = '';
                fileToUpload = null;
            }
            // Reset the global state so it can be triggered again
            ui.update(s => ({ ...s, showUploadModal: false }));
        }
    });

    async function fetchItems() {
        loading = true;
        try {
            const params: any = {
                is_trashed: isTrashed,
                is_archived: isArchived,
                shared_with_me: sharedWithMe,
                sort_by: sortKey,
                sort_order: sortOrder
            };
            
            if (currentFolderId) params.parent_id = currentFolderId;
            if (searchQuery) params.search = searchQuery;
            if (isStarred !== undefined) params.is_starred = isStarred;
            if (category) params.category = category;
            
            const response = await api.get('/items/', { params });
            items = Array.isArray(response.data) ? response.data : [];
        } catch (e) {
            toasts.error('Failed to sync with drive.');
            items = [];
        } finally {
            loading = false;
        }
    }

    async function fetchCustomCategories() {
        try {
            const response = await api.get('/categories/');
            customCategories = response.data;
        } catch (e) {}
    }

    async function fetchStorageUsage() {
        try {
            const response = await api.get('/items/storage/usage');
            storageUsage.set(response.data);
        } catch (e) {}
    }

    onMount(() => {
        fetchItems();
        fetchCustomCategories();
        fetchStorageUsage();
    });

    export function handleSearch(query: string) {
        searchQuery = query;
        fetchItems();
    }

    function toggleSelection(e: MouseEvent, itemId: string) {
        e.preventDefault();
        e.stopPropagation();
        
        const newSet = new Set(selectedItemIds);
        if (e.shiftKey || e.ctrlKey || e.metaKey) {
            if (newSet.has(itemId)) {
                newSet.delete(itemId);
            } else {
                newSet.add(itemId);
            }
        } else {
            if (newSet.has(itemId) && newSet.size === 1) {
                newSet.clear();
            } else {
                newSet.clear();
                newSet.add(itemId);
            }
        }
        selectedItemIds = newSet;
    }

    async function handleBatchAction(action: string) {
        const ids = Array.from(selectedItemIds);
        if (ids.length === 0) return;

        try {
            switch(action) {
                case 'star':
                    await Promise.all(ids.map(id => api.patch(`/items/${id}/`, { is_starred: true })));
                    toasts.success(`Starred ${ids.length} items`);
                    break;
                case 'trash':
                    await Promise.all(ids.map(id => api.delete(`/items/${id}/`)));
                    toasts.success(`Moved ${ids.length} items to trash`);
                    break;
                case 'restore':
                    await Promise.all(ids.map(id => api.patch(`/items/${id}/`, { is_trashed: false })));
                    toasts.success(`Restored ${ids.length} items`);
                    break;
                case 'download':
                    toasts.info(`Downloading ${ids.length} items...`);
                    for (const id of ids) {
                        const item = items.find(i => i.id === id);
                        if (item && !item.is_folder) await downloadFile(item);
                    }
                    break;
            }
            fetchItems();
            fetchStorageUsage();
            selectedItemIds = new Set();
        } catch (e) {
            toasts.error('Batch action failed.');
        }
    }

    function closeAllMenus() {
        showSortMenu = false;
        contextMenu = null;
    }

    async function handleAction(action: string, data?: any) {
        if (!contextMenu) return;
        const item = contextMenu.item;
        contextMenu = null;
        
        switch(action) {
            case 'star': await toggleStar(item); break;
            case 'archive': await toggleArchive(item); break;
            case 'share': sharingItem = item; break;
            case 'download': downloadFile(item); break;
            case 'trash': await moveToTrash(item); break;
            case 'restore': await restoreItem(item); break;
            case 'category': await changeCategory(item, data.name, data.id); break;
            case 'move': 
                moveTargetItem = item;
                await fetchAllFolders();
                showMoveModal = true;
                break;
        }
    }

    async function fetchAllFolders() {
        try {
            const response = await api.get('/items/', { params: { is_folder: true } });
            allFolders = response.data.filter((f: Item) => f.id !== moveTargetItem?.id);
        } catch (e) {}
    }

    async function confirmMove() {
        if (!moveTargetItem) return;
        try {
            await api.patch(`/items/${moveTargetItem.id}/`, { parent_id: selectedDestinationId });
            toasts.success(`Moved successfully`);
            showMoveModal = false;
            fetchItems();
        } catch (e) {
            toasts.error('Failed to move item.');
        }
    }

    async function toggleStar(item: Item) {
        try {
            await api.patch(`/items/${item.id}/`, { is_starred: !item.is_starred });
            items = items.map(i => i.id === item.id ? { ...i, is_starred: !i.is_starred } : i);
            toasts.success(item.is_starred ? 'Removed from favorites' : 'Added to favorites');
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    async function toggleArchive(item: Item) {
        try {
            await api.patch(`/items/${item.id}/`, { is_archived: !item.is_archived });
            items = items.filter(i => i.id !== item.id);
            toasts.success(!item.is_archived ? 'Moved to archive' : 'Restored from archive');
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    async function changeCategory(item: Item, newCat: string | null, newCatId: string | null = null) {
        try {
            await api.patch(`/items/${item.id}/`, { category: newCat, category_id: newCatId });
            items = items.map(i => i.id === item.id ? { ...i, category: newCat, category_id: newCatId } : i);
            toasts.success(`Category updated`);
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    async function moveToTrash(item: Item) {
        try {
            await api.delete(`/items/${item.id}/`);
            items = items.filter(i => i.id !== item.id);
            toasts.success(isTrashed ? 'Permanently deleted' : 'Moved to trash');
            fetchStorageUsage();
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    async function restoreItem(item: Item) {
        try {
            await api.patch(`/items/${item.id}/`, { is_trashed: false });
            items = items.filter(i => i.id !== item.id);
            toasts.success('Item restored');
            fetchStorageUsage();
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    async function downloadFile(item: Item) {
        try {
            toasts.info(`Preparing ${item.name}...`);
            const response = await api.get(`/items/${item.id}/download`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', item.name);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            toasts.success(`Downloaded ${item.name}`);
        } catch (e) {
            toasts.error('Download failed.');
        }
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

    async function emptyTrash() {
        if (!confirm('Permanently delete all items in trash?')) return;
        try {
            await api.delete('/items/trash/empty');
            items = [];
            toasts.success('Trash emptied');
            fetchStorageUsage();
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    async function createFolder() {
        if (!newFolderName) return;
        try {
            await api.post('/items/folders/', { 
                name: newFolderName, 
                parent_id: currentFolderId,
                category: selectedCategory || undefined,
                category_id: selectedCategoryId || undefined
            });
            newFolderName = '';
            showUploadModal = false;
            fetchItems();
            toasts.success('Folder created.');
        } catch (e) {
            toasts.error('Action failed.');
        }
    }

    async function uploadFile() {
        if (!fileToUpload) return;
        try {
            const formData = new FormData();
            formData.append('file', fileToUpload);
            if (currentFolderId) formData.append('parent_id', currentFolderId);
            if (selectedCategory) formData.append('category', selectedCategory);
            if (selectedCategoryId) formData.append('category_id', selectedCategoryId);
            await api.post('/items/upload/', formData);
            fileToUpload = null;
            showUploadModal = false;
            fetchItems();
            fetchStorageUsage();
            toasts.success('File uploaded.');
        } catch (e) {
            toasts.error('Upload failed.');
        }
    }

    function handleFileChange(e: Event) {
        const target = e.target as HTMLInputElement;
        if (target.files) fileToUpload = target.files[0];
    }

    function handleDrop(e: DragEvent) {
        e.preventDefault();
        isDragging = false;
        if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
            fileToUpload = e.dataTransfer.files[0];
            showUploadModal = true;
        }
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

    function openThreeDotsMenu(e: MouseEvent, item: Item) {
        e.preventDefault();
        e.stopPropagation();
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        contextMenu = { x: rect.left - 200, y: rect.bottom + 10, item };
    }

    async function handleContextMenu(e: MouseEvent, item: Item) {
        e.preventDefault();
        e.stopPropagation();
        const x = Math.min(e.clientX, window.innerWidth - 250);
        const y = Math.min(e.clientY, window.innerHeight - 450);
        contextMenu = { x, y, item };
    }
</script>

<svelte:window onclick={closeAllMenus} />

<div 
    class="flex-1 flex flex-col bg-slate-100 dark:bg-[#0f172a] overflow-hidden relative transition-colors duration-300"
    ondragover={(e) => { e.preventDefault(); isDragging = true; }}
    ondragleave={() => isDragging = false}
    ondrop={handleDrop}
>
    {#if isDragging}
        <div class="absolute inset-0 z-50 bg-indigo-600/10 dark:bg-indigo-600/20 backdrop-blur-sm flex items-center justify-center p-12" transition:fade>
            <div class="w-full h-full border-4 border-dashed border-indigo-600 dark:border-indigo-400 rounded-[40px] flex flex-col items-center justify-center text-indigo-600 dark:text-indigo-400 animate-pulse">
                <UploadCloud class="w-24 h-24 mb-6" />
                <h2 class="text-4xl font-black tracking-tighter">Drop to Upload</h2>
            </div>
        </div>
    {/if}

    <div class="flex flex-col md:flex-row md:items-center justify-between px-8 py-8 gap-4">
        <div class="flex items-center space-x-1 overflow-x-auto no-scrollbar">
            {#each breadcrumbs as crumb, i}
                <button onclick={() => navigateToBreadcrumb(crumb, i)} class={cn("flex items-center px-3 py-1.5 rounded-xl font-bold text-sm", i === breadcrumbs.length - 1 ? "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400" : "text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800")}>
                    {crumb.name === 'Root' ? 'Main Menu' : crumb.name}
                </button>
                {#if i < breadcrumbs.length - 1}<ChevronRight class="w-4 h-4 text-slate-300 dark:text-slate-700" />{/if}
            {/each}
        </div>

        <div class="flex items-center space-x-3">
            <div class="relative">
                <button onclick={(e) => { e.stopPropagation(); showSortMenu = !showSortMenu; }} class={cn("flex items-center space-x-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-[14px] px-3 py-1.5 shadow-sm font-bold text-[11px] uppercase tracking-widest", showSortMenu && "border-indigo-500")}>
                    <ArrowUpDown class="w-3 h-3" />
                    <span>Sort</span>
                </button>
                {#if showSortMenu}
                    <div class="absolute right-0 mt-2 w-64 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-2xl p-2 z-50" transition:scale={{ duration: 150, start: 0.95 }} onclick={(e) => e.stopPropagation()}>
                        <!-- Name Sorting -->
                        <div class="px-3 py-2 border-b border-slate-50 dark:border-slate-800 mb-1 font-bold text-[10px] text-slate-400 uppercase tracking-widest">Name</div>
                        <button 
                            onclick={() => { sortKey = 'name'; sortOrder = 'asc'; fetchItems(); showSortMenu = false; }} 
                            class={cn("w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold", sortKey === 'name' && sortOrder === 'asc' ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20" : "text-slate-600 dark:text-slate-300")}
                        >
                            <span>A to Z</span>
                            {#if sortKey === 'name' && sortOrder === 'asc'}<ArrowUp class="w-3 h-3" />{/if}
                        </button>
                        <button 
                            onclick={() => { sortKey = 'name'; sortOrder = 'desc'; fetchItems(); showSortMenu = false; }} 
                            class={cn("w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold", sortKey === 'name' && sortOrder === 'desc' ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20" : "text-slate-600 dark:text-slate-300")}
                        >
                            <span>Z to A</span>
                            {#if sortKey === 'name' && sortOrder === 'desc'}<ArrowDown class="w-3 h-3" />{/if}
                        </button>

                        <!-- Date Sorting -->
                        <div class="px-3 py-2 border-b border-slate-50 dark:border-slate-800 mt-2 mb-1 font-bold text-[10px] text-slate-400 uppercase tracking-widest">Date Modified</div>
                        <button 
                            onclick={() => { sortKey = 'date'; sortOrder = 'desc'; fetchItems(); showSortMenu = false; }} 
                            class={cn("w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold", sortKey === 'date' && sortOrder === 'desc' ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20" : "text-slate-600 dark:text-slate-300")}
                        >
                            <span>Newest First</span>
                            {#if sortKey === 'date' && sortOrder === 'desc'}<ArrowDown class="w-3 h-3" />{/if}
                        </button>
                        <button 
                            onclick={() => { sortKey = 'date'; sortOrder = 'asc'; fetchItems(); showSortMenu = false; }} 
                            class={cn("w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold", sortKey === 'date' && sortOrder === 'asc' ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20" : "text-slate-600 dark:text-slate-300")}
                        >
                            <span>Oldest First</span>
                            {#if sortKey === 'date' && sortOrder === 'asc'}<ArrowUp class="w-3 h-3" />{/if}
                        </button>

                        <!-- Size Sorting -->
                        <div class="px-3 py-2 border-b border-slate-50 dark:border-slate-800 mt-2 mb-1 font-bold text-[10px] text-slate-400 uppercase tracking-widest">File Size</div>
                        <button 
                            onclick={() => { sortKey = 'size'; sortOrder = 'desc'; fetchItems(); showSortMenu = false; }} 
                            class={cn("w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold", sortKey === 'size' && sortOrder === 'desc' ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20" : "text-slate-600 dark:text-slate-300")}
                        >
                            <span>Largest First</span>
                            {#if sortKey === 'size' && sortOrder === 'desc'}<ArrowDown class="w-3 h-3" />{/if}
                        </button>
                        <button 
                            onclick={() => { sortKey = 'size'; sortOrder = 'asc'; fetchItems(); showSortMenu = false; }} 
                            class={cn("w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold", sortKey === 'size' && sortOrder === 'asc' ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20" : "text-slate-600 dark:text-slate-300")}
                        >
                            <span>Smallest First</span>
                            {#if sortKey === 'size' && sortOrder === 'asc'}<ArrowUp class="w-3 h-3" />{/if}
                        </button>
                    </div>
                {/if}
            </div>

            <div class="flex bg-white dark:bg-slate-800 p-1 rounded-[14px] border border-slate-200 dark:border-slate-700 shadow-sm">
                <button onclick={() => viewMode = 'list'} class={cn("p-1.5 rounded-lg flex items-center space-x-1.5 px-2.5", viewMode === 'list' ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500")}><LayoutList class="w-3.5 h-3.5" /></button>
                <button onclick={() => viewMode = 'grid'} class={cn("p-1.5 rounded-lg flex items-center space-x-1.5 px-2.5", viewMode === 'grid' ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500")}><LayoutGrid class="w-3.5 h-3.5" /></button>
            </div>
            
            {#if isTrashed}
                <button onclick={emptyTrash} class="flex items-center justify-center space-x-3 bg-rose-600 hover:bg-rose-700 text-white rounded-[24px] px-10 py-4 shadow-2xl font-bold uppercase tracking-widest transition-all">
                    <Trash class="w-5 h-5 stroke-[3px]" />
                    <span class="text-sm">Empty Trash</span>
                </button>
            {/if}
        </div>
    </div>

    <main class="flex-1 overflow-y-auto px-8 pb-12 custom-scrollbar">
        {#if loading}
            <div class="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-6">
                {#each Array(12) as _}<div class="bg-white/50 dark:bg-slate-800/30 h-48 rounded-[40px] animate-pulse"></div>{/each}
            </div>
        {:else if items.length === 0}
            <div class="flex flex-col items-center justify-center h-[50vh] text-center" in:fade>
                <div class="relative mb-8">
                    <div class="bg-indigo-600/5 w-32 h-32 rounded-[40px] flex items-center justify-center animate-bounce duration-[3000ms]"><UploadCloud class="w-16 h-16 text-indigo-200 dark:text-indigo-900/40" /></div>
                </div>
                <h3 class="text-3xl font-black text-slate-900 dark:text-white tracking-tighter mb-3">Your Cloud is Ready</h3>
                <p class="text-slate-500 dark:text-slate-400 font-medium">Use the "Create New" button to get started.</p>
            </div>
        {:else if viewMode === 'list'}
            <div class="bg-slate-50/80 dark:bg-slate-900 rounded-[32px] border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden" in:fly={{ y: 20, duration: 400 }}>
                <table class="w-full text-left">
                    <thead>
                        <tr class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] border-b border-slate-50 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
                            <th class="py-5 px-8">File Name</th>
                            <th class="py-5 px-8">Date</th>
                            <th class="py-5 px-8">Size</th>
                            <th class="py-5 px-8 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-50 dark:divide-slate-800">
                        {#each items as item (item.id)}
                            {@const Icon = getFileIcon(item)}
                            <tr class={cn("group hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-colors cursor-pointer", selectedItemIds.has(item.id) && "bg-indigo-50/50 dark:bg-indigo-900/20")} onclick={(e) => item.is_folder ? openFolder(item) : toggleSelection(e, item.id)} ondblclick={() => item.is_folder ? openFolder(item) : (previewItem = item)}>
                                <td class="py-5 px-8">
                                    <div class="flex items-center space-x-5">
                                        <div class={cn("p-3 rounded-2xl relative", item.is_folder ? "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400" : "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400")}><svelte:component this={Icon} class={cn("w-5 h-5", item.is_folder && "fill-current")} /></div>
                                        <div class="min-w-0"><span class="font-black text-sm truncate dark:text-white">{item.name}</span></div>
                                    </div>
                                </td>
                                <td class="py-5 px-8 text-xs font-bold text-slate-500 dark:text-slate-400">{new Date(item.updated_at).toLocaleDateString()}</td>
                                <td class="py-5 px-8 text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase">{item.is_folder ? 'CONTAINER' : formatSize(item.size)}</td>
                                <td class="py-5 px-8 text-right">
                                    <button onclick={(e) => { e.stopPropagation(); openThreeDotsMenu(e, item); }} class="p-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 transition-colors"><MoreHorizontal class="w-5 h-5" /></button>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {:else}
            <div class="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-8" in:fly={{ y: 20, duration: 400 }}>
                {#each items as item (item.id)}
                    {@const Icon = getFileIcon(item)}
                    <div 
                        class={cn(
                            "group bg-slate-50/50 dark:bg-slate-800/40 p-6 rounded-[40px] border-2 border-transparent transition-all relative cursor-pointer flex flex-col items-center text-center", 
                            selectedItemIds.has(item.id) ? "border-indigo-500 bg-white dark:bg-slate-800 shadow-2xl shadow-indigo-500/10 scale-[1.02]" : "hover:bg-white dark:hover:bg-slate-800 border-slate-200 dark:border-slate-800 shadow-sm"
                        )} 
                        onclick={(e) => item.is_folder ? openFolder(item) : toggleSelection(e, item.id)} 
                        ondblclick={() => item.is_folder ? openFolder(item) : (previewItem = item)}
                    >
                        <div class="absolute top-4 right-4 z-20 flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            {#if !item.is_folder}<button onclick={(e) => { e.stopPropagation(); downloadFile(item); }} class="p-2 rounded-xl bg-white/80 dark:bg-slate-800/80 backdrop-blur text-slate-400 hover:text-indigo-600 shadow-sm border border-slate-100 dark:border-slate-700 transition-all"><Download class="w-4 h-4" /></button>{/if}
                            <button onclick={(e) => { e.stopPropagation(); openThreeDotsMenu(e, item); }} class="p-2 rounded-xl bg-white/80 dark:bg-slate-800/80 backdrop-blur text-slate-400 hover:text-indigo-600 shadow-sm border border-slate-100 dark:border-slate-700 transition-all"><MoreVertical class="w-4 h-4" /></button>
                        </div>
                        <div class={cn("w-20 h-20 flex items-center justify-center rounded-[32px] mb-6", item.is_folder ? "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400" : "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400")}>
                            <svelte:component this={Icon} class={cn("w-10 h-10 transition-transform duration-500", item.is_folder && "fill-current")} />
                            {#if item.is_starred}
                                <div class="absolute top-2 left-2 bg-white dark:bg-slate-900 rounded-xl p-1.5 shadow-lg border border-slate-100 dark:border-slate-800 animate-in zoom-in-50 duration-300">
                                    <Star class="w-4 h-4 text-amber-500 fill-current" />
                                </div>
                            {/if}
                        </div>
                        <div class="w-full"><h4 class="font-black text-sm truncate px-1 dark:text-white tracking-tight mb-1">{item.name}</h4><p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">{item.is_folder ? 'Container' : formatSize(item.size)}</p></div>
                    </div>
                {/each}
            </div>
        {/if}
    </main>
</div>

{#if showUploadModal}
    <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[60] p-6" transition:fade>
        <div class="bg-white dark:bg-slate-900 rounded-[48px] p-10 w-full max-w-xl shadow-2xl relative overflow-hidden" transition:fly={{ y: 40, duration: 400 }}>
            <button onclick={() => { showUploadModal = false; fileToUpload = null; }} class="absolute top-8 right-8 p-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-2xl text-slate-400 transition-all"><X class="w-6 h-6" /></button>
            <div class="flex items-center space-x-4 mb-12">
                <div class="bg-indigo-600 p-3.5 rounded-[24px] shadow-xl shadow-indigo-200"><Plus class="w-7 h-7 text-white stroke-[3px]" /></div>
                <div><h2 class="text-3xl font-black tracking-tighter leading-none mb-1 dark:text-white">{fileToUpload || !newFolderName ? 'Upload Data' : 'New Folder'}</h2><p class="text-slate-400 font-bold text-xs uppercase tracking-widest">DRIVE X SYSTEM</p></div>
            </div>
            <div class="space-y-8">
                {#if !fileToUpload && newFolderName}
                    <div><label for="folder-name" class="block text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4 ml-1">Folder Name</label><div class="flex space-x-3"><input id="folder-name" bind:value={newFolderName} type="text" placeholder="Folder label..." class="w-full bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent rounded-[24px] px-6 py-4 text-sm font-bold outline-none dark:text-white focus:bg-white dark:focus:bg-slate-900 focus:border-indigo-500/30 transition-all" /><button onclick={createFolder} class="bg-indigo-600 hover:bg-indigo-700 text-white px-8 rounded-[24px] text-sm font-black transition-all shadow-xl shadow-indigo-500/20 uppercase tracking-widest">CREATE</button></div></div>
                {:else}
                    <div><div class={cn("relative bg-slate-50 dark:bg-slate-800/30 border-4 border-dashed rounded-[40px] p-12 transition-all", fileToUpload ? "border-indigo-500 bg-indigo-50/30" : "border-slate-200 dark:border-slate-700")}><input id="file-upload" type="file" onchange={handleFileChange} class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" /><div class="text-center"><div class={cn("w-20 h-20 rounded-[32px] flex items-center justify-center mx-auto mb-6 transition-all", fileToUpload ? "bg-indigo-600 text-white" : "bg-white dark:bg-slate-800 text-indigo-500")}><UploadCloud class="w-10 h-10" /></div><h3 class="text-lg font-black mb-1 dark:text-white tracking-tight">{fileToUpload ? fileToUpload.name : 'Choose File'}</h3><p class="text-xs font-bold text-slate-400 uppercase tracking-widest">{fileToUpload ? formatSize(fileToUpload.size) : 'Drag or Click'}</p></div></div>{#if fileToUpload}<button onclick={uploadFile} class="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white py-5 rounded-[28px] text-lg font-black transition-all flex items-center justify-center space-x-3 shadow-2xl shadow-indigo-500/20 active:scale-[0.98]"><span>UPLOAD TO NODE</span><ArrowLeft class="w-6 h-6 rotate-180" /></button>{/if}</div>
                {/if}
            </div>
        </div>
    </div>
{/if}

{#if contextMenu}<ContextMenu x={contextMenu.x} y={contextMenu.y} item={contextMenu.item} categories={customCategories} onclose={() => contextMenu = null} onaction={handleAction} />{/if}
{#if showMoveModal}<div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[70] p-6" transition:fade><div class="bg-white dark:bg-slate-900 rounded-[48px] p-10 w-full max-w-md shadow-2xl relative overflow-hidden border border-white/10"><div class="flex items-center justify-between mb-8"><div class="flex items-center space-x-4"><div class="bg-indigo-100 dark:bg-indigo-900/30 p-2.5 rounded-2xl"><Folder class="w-6 h-6 text-indigo-600 dark:text-indigo-400" /></div><h2 class="text-xl font-black tracking-tight dark:text-white uppercase tracking-widest">Move Item</h2></div><button onclick={() => showMoveModal = false} class="p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-slate-400 transition-colors"><X class="w-5 h-5" /></button></div><div class="space-y-6"><div class="max-h-60 overflow-y-auto space-y-2 pr-2 custom-scrollbar"><button onclick={() => selectedDestinationId = null} class={cn("w-full flex items-center space-x-3 p-4 rounded-2xl border-2 transition-all font-bold text-sm", selectedDestinationId === null ? "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-500 text-indigo-600 dark:text-indigo-400" : "bg-slate-50 dark:bg-slate-800/30 border-transparent text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800")}>Main Drive</button>{#each allFolders as folder}<button onclick={() => selectedDestinationId = folder.id} class={cn("w-full flex items-center space-x-3 p-4 rounded-2xl border-2 transition-all font-bold text-sm", selectedDestinationId === folder.id ? "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-500 text-indigo-600 dark:text-indigo-400" : "bg-slate-50 dark:bg-slate-800/30 border-transparent text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800")}>{folder.name}</button>{/each}</div><button onclick={confirmMove} class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-[24px] py-4 transition-all shadow-xl shadow-indigo-500/20 uppercase tracking-widest text-sm">Confirm Relocation</button></div></div></div>{/if}
{#if sharingItem}<ShareModal item={sharingItem} onclose={() => sharingItem = null} />{/if}
{#if previewItem}<FilePreview item={previewItem} onclose={() => previewItem = null} ondownload={() => downloadFile(previewItem!)} />{/if}
{#if selectedItemIds.size > 0}<div class="fixed bottom-10 left-1/2 -translate-x-1/2 z-[80] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[32px] shadow-2xl p-3 flex items-center space-x-6 min-w-[400px]" transition:fly={{ y: 100, duration: 500, easing: quintOut }}><div class="flex items-center space-x-4 pl-6 pr-4 border-r border-slate-100 dark:border-slate-800"><div class="bg-indigo-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-black text-xs shadow-lg shadow-indigo-500/20">{selectedItemIds.size}</div><span class="text-xs font-black text-slate-900 dark:text-white uppercase tracking-widest">Selected</span></div><div class="flex items-center space-x-2"><button onclick={() => handleBatchAction('star')} class="p-3 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-2xl text-slate-400 hover:text-amber-500 transition-all flex flex-col items-center"><Star class="w-5 h-5 mb-1" /><span class="text-[8px] font-black uppercase tracking-tighter">Favorite</span></button><button onclick={() => handleBatchAction('download')} class="p-3 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-2xl text-slate-400 hover:text-indigo-600 transition-all flex flex-col items-center"><Download class="w-5 h-5 mb-1" /><span class="text-[8px] font-black uppercase tracking-tighter">Download</span></button><button onclick={() => handleBatchAction('trash')} class="p-3 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-2xl text-slate-400 hover:text-rose-600 transition-all flex flex-col items-center"><Trash class="w-5 h-5 mb-1" /><span class="text-[8px] font-black uppercase tracking-tighter">Delete</span></button></div><div class="pl-4 pr-3"><button onclick={() => selectedItemIds = new Set()} class="p-3 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-2xl text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all"><X class="w-6 h-6" /></button></div></div>{/if}

<style>
    @reference "../../routes/layout.css";
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    .custom-scrollbar::-webkit-scrollbar { width: 4px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
    .custom-scrollbar::-webkit-scrollbar-thumb { @apply bg-slate-200 dark:bg-slate-800 rounded-full; }
</style>
