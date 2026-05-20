<script lang="ts">
    import { onMount } from 'svelte';
    import api, { BASE_URL } from '$lib/api';
    import { storageUsage } from '$lib/stores';
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
    import { toasts } from '$lib/toasts';
    import ShareModal from './ShareModal.svelte';
    import ContextMenu from './ContextMenu.svelte';

    interface Item {
        id: string;
        name: string;
        is_folder: boolean;
        size?: number;
        mime_type?: string;
        is_starred: boolean;
        is_trashed: boolean;
        is_archived: boolean;
        category?: string;
        category_id?: string;
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

    let items = $state<Item[]>([]);
    let loading = $state(true);
    let viewMode = $state<'list' | 'grid'>('grid');
    let searchQuery = $state('');
    let sortKey = $state<'name' | 'size' | 'date'>('name');
    let sortOrder = $state<'asc' | 'desc'>('asc');
    let showSortMenu = $state(false);
    let showCreateMenu = $state(false);
    let currentFolderId = $state<string | null>(null);
    let breadcrumbs = $state<{id: string | null, name: string}[]>([{id: null, name: 'Root'}]);
    
    let showUploadModal = $state(false);
    let newFolderName = $state('');
    let selectedCategory = $state<string | null>(null);
    let selectedCategoryId = $state<string | null>(null);
    let fileToUpload = $state<File | null>(null);
    let selectedItemId = $state<string | null>(null);
    let isDragging = $state(false);
    let sharingItem = $state<Item | null>(null);
    let customCategories = $state<any[]>([]);

    let showMoveModal = $state(false);
    let moveTargetItem = $state<Item | null>(null);
    let allFolders = $state<Item[]>([]);
    let selectedDestinationId = $state<string | null>(null);

    // Context Menu State
    let contextMenu = $state<{ x: number, y: number, item: Item } | null>(null);

    async function handleContextMenu(e: MouseEvent, item: Item) {
        e.preventDefault();
        e.stopPropagation();
        
        // Adjust position if too close to edges
        const x = Math.min(e.clientX, window.innerWidth - 250);
        const y = Math.min(e.clientY, window.innerHeight - 450);
        
        contextMenu = { x, y, item };
    }

    function openThreeDotsMenu(e: MouseEvent, item: Item) {
        e.preventDefault();
        e.stopPropagation();
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        contextMenu = { x: rect.left - 200, y: rect.bottom + 10, item };
    }

    function closeAllMenus() {
        showSortMenu = false;
        showCreateMenu = false;
        contextMenu = null;
    }

    async function handleAction(action: string, data?: any) {
        if (!contextMenu) return;
        const item = contextMenu.item;
        
        // Close menu first to ensure responsiveness
        contextMenu = null;
        
        switch(action) {
            case 'star': await toggleStar(item); break;
            case 'archive': await toggleArchive(item); break;
            case 'share': openShareModal(item); break;
            case 'download': downloadFile(item); break;
            case 'trash': await moveToTrash(item); break;
            case 'restore': await restoreItem(item); break;
            case 'category': await changeCategory(item, data.name, data.id); break;
            case 'details': 
                toasts.info(`File details for ${item.name} coming soon`);
                break;
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

    async function fetchStorageUsage() {
        try {
            const response = await api.get('/items/storage/usage');
            storageUsage.set(response.data);
        } catch (e) {}
    }

    async function confirmMove() {
        if (!moveTargetItem) return;
        try {
            await api.patch(`/items/${moveTargetItem.id}/`, { parent_id: selectedDestinationId });
            toasts.success(`Moved ${moveTargetItem.name} successfully`);
            showMoveModal = false;
            fetchItems();
            fetchStorageUsage();
        } catch (e) {
            toasts.error('Failed to move item.');
        }
    }

    async function fetchCustomCategories() {
        try {
            const response = await api.get('/categories/');
            customCategories = response.data;
        } catch (e) {
            // Silently fail
        }
    }

    async function fetchItems() {
        loading = true;
        try {
            const params = {
                parent_id: currentFolderId || undefined,
                search: searchQuery || undefined,
                is_starred: isStarred,
                is_trashed: isTrashed,
                is_archived: isArchived,
                category: category || undefined,
                shared_with_me: sharedWithMe,
                sort_by: sortKey,
                sort_order: sortOrder
            };
            const response = await api.get('/items/', { params });
            items = Array.isArray(response.data) ? response.data : [];
        } catch (e) {
            console.error('Fetch error:', e);
            toasts.error('Failed to sync with drive.');
            items = [];
        } finally {
            loading = false;
        }
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
            await api.patch(`/items/${item.id}/`, { 
                category: newCat,
                category_id: newCatId
            });
            items = items.map(i => i.id === item.id ? { ...i, category: newCat, category_id: newCatId } : i);
            toasts.success(`Category updated to ${newCat || 'None'}`);
        } catch (e) {
            toasts.error('Failed to update category.');
        }
    }

    async function moveToTrash(item: Item) {
        try {
            await api.delete(`/items/${item.id}/`);
            items = items.filter(i => i.id !== item.id);
            toasts.success(isTrashed ? 'Permanently deleted' : 'Moved to trash');
            fetchStorageUsage();
        } catch (e: any) {
            console.error('Delete error:', e);
            toasts.error(e.response?.data?.detail || 'Action failed.');
        }
    }

    async function restoreItem(item: Item) {
        try {
            await api.patch(`/items/${item.id}/`, { is_trashed: false });
            items = items.filter(i => i.id !== item.id);
            toasts.success('Item restored successfully');
            fetchStorageUsage();
        } catch (e: any) {
            console.error('Restore error:', e);
            toasts.error(e.response?.data?.detail || 'Failed to restore item.');
        }
    }

    function downloadFile(item: Item) {
        window.open(`${BASE_URL}/items/${item.id}/download/`, '_blank');
        toasts.info(`Downloading ${item.name}...`);
    }

    async function openShareModal(item: Item) {
        sharingItem = item;
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
            await api.post('/items/folders/', { 
                name: newFolderName, 
                parent_id: currentFolderId,
                category: selectedCategory || undefined,
                category_id: selectedCategoryId || undefined
            });
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
            if (selectedCategory) formData.append('category', selectedCategory);
            if (selectedCategoryId) formData.append('category_id', selectedCategoryId);
            
            await api.post('/items/upload/', formData);
            fileToUpload = null;
            showUploadModal = false;
            fetchItems();
            fetchStorageUsage();
            toasts.success('File uploaded to drive.');
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

<svelte:window onclick={closeAllMenus} />

<div 
    class="flex-1 flex flex-col bg-slate-100 dark:bg-[#0f172a] overflow-hidden relative transition-colors duration-300"
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
                        {crumb.name === 'Root' ? 'Main Menu' : crumb.name}
                    </button>
                    {#if i < breadcrumbs.length - 1}
                        <ChevronRight class="w-4 h-4 text-slate-300 dark:text-slate-700 shrink-0" />
                    {/if}
                {/each}
            </div>
        </div>

        <div class="flex items-center space-x-3">
            <!-- Sort Switcher -->
            <div class="relative">
                <button 
                    onclick={(e) => { e.stopPropagation(); showSortMenu = !showSortMenu; showCreateMenu = false; }}
                    class={cn(
                        "flex items-center space-x-1.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-[14px] px-3 py-1.5 shadow-sm transition-all font-bold text-[11px] uppercase tracking-widest hover:bg-slate-200 dark:hover:bg-slate-700",
                        showSortMenu && "border-indigo-500 ring-2 ring-indigo-500/10"
                    )}
                >
                    <ArrowUpDown class="w-3 h-3" />
                    <span>Sort</span>
                </button>

                {#if showSortMenu}
                    <div 
                        class="absolute right-0 mt-2 w-64 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-2xl p-2 z-50 overflow-hidden"
                        transition:scale={{ duration: 150, start: 0.95 }}
                        onmouseleave={() => showSortMenu = false}
                        onclick={(e) => e.stopPropagation()}
                    >
                        <!-- Name Sorting -->
                        <div class="px-3 py-2 border-b border-slate-50 dark:border-slate-800 mb-1">
                            <div class="flex items-center space-x-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                <Type class="w-3 h-3" />
                                <span>Name</span>
                            </div>
                        </div>
                        <button 
                            onclick={() => { sortKey = 'name'; sortOrder = 'asc'; fetchItems(); showSortMenu = false; }}
                            class={cn(
                                "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all group",
                                (sortKey === 'name' && sortOrder === 'asc') ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400" : "hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                            )}
                        >
                            <span class="text-xs font-bold">Alphabetical (A to Z)</span>
                            {#if sortKey === 'name' && sortOrder === 'asc'}<ArrowUp class="w-3 h-3" />{/if}
                        </button>
                        <button 
                            onclick={() => { sortKey = 'name'; sortOrder = 'desc'; fetchItems(); showSortMenu = false; }}
                            class={cn(
                                "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all group mb-2",
                                (sortKey === 'name' && sortOrder === 'desc') ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400" : "hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                            )}
                        >
                            <span class="text-xs font-bold">Alphabetical (Z to A)</span>
                            {#if sortKey === 'name' && sortOrder === 'desc'}<ArrowDown class="w-3 h-3" />{/if}
                        </button>

                        <!-- Date Sorting -->
                        <div class="px-3 py-2 border-b border-slate-50 dark:border-slate-800 mb-1">
                            <div class="flex items-center space-x-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                <Calendar class="w-3 h-3" />
                                <span>Modification Date</span>
                            </div>
                        </div>
                        <button 
                            onclick={() => { sortKey = 'date'; sortOrder = 'desc'; fetchItems(); showSortMenu = false; }}
                            class={cn(
                                "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all group",
                                (sortKey === 'date' && sortOrder === 'desc') ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400" : "hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                            )}
                        >
                            <span class="text-xs font-bold">Newest First</span>
                            {#if sortKey === 'date' && sortOrder === 'desc'}<ArrowDown class="w-3 h-3" />{/if}
                        </button>
                        <button 
                            onclick={() => { sortKey = 'date'; sortOrder = 'asc'; fetchItems(); showSortMenu = false; }}
                            class={cn(
                                "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all group mb-2",
                                (sortKey === 'date' && sortOrder === 'asc') ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400" : "hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                            )}
                        >
                            <span class="text-xs font-bold">Oldest First</span>
                            {#if sortKey === 'date' && sortOrder === 'asc'}<ArrowUp class="w-3 h-3" />{/if}
                        </button>

                        <!-- Size Sorting -->
                        <div class="px-3 py-2 border-b border-slate-50 dark:border-slate-800 mb-1">
                            <div class="flex items-center space-x-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                <HardDrive class="w-3 h-3" />
                                <span>File Size</span>
                            </div>
                        </div>
                        <button 
                            onclick={() => { sortKey = 'size'; sortOrder = 'desc'; fetchItems(); showSortMenu = false; }}
                            class={cn(
                                "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all group",
                                (sortKey === 'size' && sortOrder === 'desc') ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400" : "hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                            )}
                        >
                            <span class="text-xs font-bold">Largest First</span>
                            {#if sortKey === 'size' && sortOrder === 'desc'}<ArrowDown class="w-3 h-3" />{/if}
                        </button>
                        <button 
                            onclick={() => { sortKey = 'size'; sortOrder = 'asc'; fetchItems(); showSortMenu = false; }}
                            class={cn(
                                "w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all group",
                                (sortKey === 'size' && sortOrder === 'asc') ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400" : "hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300"
                            )}
                        >
                            <span class="text-xs font-bold">Smallest First</span>
                            {#if sortKey === 'size' && sortOrder === 'asc'}<ArrowUp class="w-3 h-3" />{/if}
                        </button>
                    </div>
                {/if}
            </div>

            <!-- View Mode Switcher -->
            <div class="flex bg-white dark:bg-slate-800 p-1 rounded-[14px] border border-slate-200/50 dark:border-slate-700/50 shadow-sm">
                <button 
                    onclick={() => viewMode = 'list'}
                    class={cn(
                        "p-1.5 rounded-lg transition-all flex items-center space-x-1.5 px-2.5", 
                        viewMode === 'list' 
                            ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 shadow-inner" 
                            : "text-slate-400 dark:text-slate-500 hover:text-slate-600"
                    )}
                >
                    <LayoutList class="w-3.5 h-3.5" />
                    <span class="text-[10px] font-black uppercase tracking-widest hidden lg:block">List</span>
                </button>
                <button 
                    onclick={() => viewMode = 'grid'}
                    class={cn(
                        "p-1.5 rounded-lg transition-all flex items-center space-x-1.5 px-2.5", 
                        viewMode === 'grid' 
                            ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 shadow-inner" 
                            : "text-slate-400 dark:text-slate-500 hover:text-slate-600"
                    )}
                >
                    <LayoutGrid class="w-3.5 h-3.5" />
                    <span class="text-[10px] font-black uppercase tracking-widest hidden lg:block">Grid</span>
                </button>
            </div>
            
            <!-- Create New Switcher -->
            <div class="relative">
                <button 
                    onclick={(e) => { e.stopPropagation(); showCreateMenu = !showCreateMenu; showSortMenu = false; }}
                    class={cn(
                        "flex items-center justify-center space-x-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-[24px] px-10 py-4 shadow-2xl shadow-indigo-500/30 dark:shadow-none transition-all active:scale-[0.98] font-bold uppercase tracking-widest",
                        showCreateMenu && "ring-4 ring-indigo-500/10"
                    )}
                >
                    <Plus class="w-5 h-5 stroke-[3px]" />
                    <span class="text-sm">Create New</span>
                    <ChevronDown class="w-4 h-4 ml-1 opacity-70" />
                </button>

                {#if showCreateMenu}
                    <div 
                        class="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-2xl p-2 z-50 overflow-hidden"
                        transition:scale={{ duration: 150, start: 0.95 }}
                        onmouseleave={() => showCreateMenu = false}
                        onclick={(e) => e.stopPropagation()}
                    >
                        <button 
                            onclick={() => { showUploadModal = true; selectedCategory = null; selectedCategoryId = null; fileToUpload = null; newFolderName = 'New Folder'; showCreateMenu = false; }}
                            class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all group"
                        >
                            <FolderPlus class="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
                            <span class="text-xs font-bold">New Folder</span>
                        </button>
                        <button 
                            onclick={() => { showUploadModal = true; selectedCategory = null; selectedCategoryId = null; fileToUpload = null; newFolderName = ''; showCreateMenu = false; }}
                            class="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all group"
                        >
                            <UploadCloud class="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
                            <span class="text-xs font-bold">Upload File</span>
                        </button>
                    </div>
                {/if}
            </div>
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
                    Organize your files, collaborate with your team, and access your data from anywhere in the universe.
                </p>
                <button 
                    onclick={() => showUploadModal = true}
                    class="mt-10 px-8 py-4 bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 font-black rounded-2xl border-2 border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all shadow-sm"
                >
                    Upload Your First File
                </button>
            </div>
        {:else if viewMode === 'list'}
            <div class="bg-white dark:bg-slate-900 rounded-[32px] border border-slate-200/50 dark:border-slate-800 shadow-sm overflow-hidden" in:fly={{ y: 20, duration: 400 }}>
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] border-b border-slate-50 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30">
                            <th class="py-5 px-8">File Name</th>
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
                                            "p-3 rounded-2xl transition-all shadow-sm group-hover:scale-110 relative",
                                            item.is_folder 
                                                ? "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400" 
                                                : "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400"
                                        )}>
                                            <svelte:component this={Icon} class={cn("w-5 h-5", item.is_folder && "fill-current")} />
                                            {#if item.is_starred}
                                                <div class="absolute -top-1 -right-1 bg-white dark:bg-slate-900 rounded-full p-0.5 shadow-sm border border-slate-100 dark:border-slate-800">
                                                    <Star class="w-2.5 h-2.5 text-amber-500 fill-current" />
                                                </div>
                                            {/if}
                                        </div>
                                        <div class="flex flex-col min-w-0">
                                            {#if item.is_folder}
                                                <button onclick={(e) => { e.stopPropagation(); openFolder(item); }} class="font-black text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors text-sm truncate tracking-tight text-left">{item.name}</button>
                                            {:else}
                                                <span class="font-black text-slate-900 dark:text-white text-sm truncate tracking-tight">{item.name}</span>
                                            {/if}
                                            <div class="flex items-center space-x-2 mt-1">
                                                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter truncate">
                                                    {item.is_folder ? 'Folder Container' : item.mime_type || 'Unclassified Data'}
                                                </span>
                                                {#if item.category}
                                                    <span class="text-[8px] px-1.5 py-0.5 rounded-md font-black uppercase tracking-widest bg-indigo-100 text-indigo-600 dark:bg-indigo-900/40 dark:text-indigo-400">
                                                        {item.category}
                                                    </span>
                                                {/if}
                                            </div>
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
                                    <button 
                                        onclick={(e) => openThreeDotsMenu(e, item)}
                                        class="p-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-indigo-600 transition-all"
                                    >
                                        <MoreHorizontal class="w-5 h-5" />
                                    </button>
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
                        <!-- Quick Menu Trigger -->
                        <div class="absolute top-4 right-4 z-20">
                            <button 
                                onclick={(e) => openThreeDotsMenu(e, item)}
                                class="p-2 rounded-xl bg-white/80 dark:bg-slate-800/80 backdrop-blur shadow-sm border border-slate-100 dark:border-slate-700 text-slate-400 hover:text-indigo-600 transition-all"
                            >
                                <MoreVertical class="w-4 h-4" />
                            </button>
                        </div>

                        <div class={cn(
                            "w-20 h-20 flex items-center justify-center rounded-[32px] mb-6 transition-all duration-500 group-hover:rotate-6 shadow-sm relative",
                            item.is_folder 
                                ? "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 group-hover:bg-amber-200" 
                                : "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 group-hover:bg-indigo-200"
                        )}>
                            <svelte:component this={Icon} class={cn("w-10 h-10 transition-transform duration-500", item.is_folder && "fill-current")} />
                            {#if item.is_starred}
                                <div class="absolute top-2 left-2 bg-white dark:bg-slate-900 rounded-xl p-1.5 shadow-lg border border-slate-100 dark:border-slate-800 animate-in zoom-in-50 duration-300">
                                    <Star class="w-4 h-4 text-amber-500 fill-current" />
                                </div>
                            {/if}
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
                <button onclick={() => { showUploadModal = false; fileToUpload = null; selectedCategory = null; selectedCategoryId = null; }} class="p-3 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-2xl text-slate-400 transition-all active:scale-90">
                    <X class="w-6 h-6" />
                </button>
            </div>

            <div class="flex items-center space-x-4 mb-12">
                <div class="bg-indigo-600 p-3.5 rounded-[24px] shadow-xl shadow-indigo-200 dark:shadow-none">
                    <Plus class="w-7 h-7 text-white stroke-[3px]" />
                </div>
                <div>
                    <h2 class="text-3xl font-black text-slate-900 dark:text-white tracking-tighter leading-none mb-1">{fileToUpload || !newFolderName ? 'Upload New File' : 'Create New Folder'}</h2>
                    <p class="text-slate-400 dark:text-slate-500 font-bold text-xs uppercase tracking-widest">Storage Management System</p>
                </div>
            </div>
            
            <div class="space-y-8">
                <!-- Category Selection -->
                <div>
                    <label class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-4">Assign Category</label>
                    <div class="grid grid-cols-3 gap-3">
                        <button 
                            onclick={() => { selectedCategory = null; selectedCategoryId = null; }}
                            class={cn(
                                "flex items-center justify-center space-x-3 p-3 rounded-2xl border-2 transition-all font-bold text-xs",
                                (selectedCategory === null && !selectedCategoryId) 
                                    ? "bg-slate-200 border-slate-400 text-slate-700 dark:bg-slate-700 dark:text-slate-200 shadow-inner" 
                                    : "bg-slate-50 dark:bg-slate-800/50 border-transparent text-slate-500 hover:border-slate-200 dark:hover:border-slate-700"
                            )}
                        >
                            <X class="w-3 h-3" />
                            <span>None</span>
                        </button>
                        
                        {#each customCategories as cat}
                            <button 
                                onclick={() => { selectedCategoryId = cat.id; selectedCategory = cat.name; }}
                                class={cn(
                                    "flex items-center justify-center space-x-3 p-3 rounded-2xl border-2 transition-all font-bold text-xs",
                                    selectedCategoryId === cat.id 
                                        ? `${cat.color} border-indigo-500 text-white shadow-inner` 
                                        : "bg-slate-50 dark:bg-slate-800/50 border-transparent text-slate-500 hover:border-slate-200 dark:hover:border-slate-700"
                                )}
                            >
                                <div class="w-2 h-2 rounded-full bg-white/50"></div>
                                <span class="truncate">{cat.name}</span>
                            </button>
                        {/each}
                    </div>
                </div>

                {#if !fileToUpload && newFolderName}
                    <!-- Create Folder Section -->
                    <div>
                        <label for="folder-name" class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-4">Folder Name</label>
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
                            <button onclick={createFolder} class="bg-indigo-600 hover:bg-indigo-700 text-white px-8 rounded-[24px] text-sm font-black transition-all active:scale-95 shadow-xl shadow-slate-200 dark:shadow-none">CREATE</button>
                        </div>
                    </div>
                {:else}
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
                                <span>UPLOAD FILE</span>
                                <ArrowLeft class="w-6 h-6 rotate-180" />
                            </button>
                        {/if}
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}

<!-- Context Menu -->
{#if contextMenu}
    <ContextMenu 
        x={contextMenu.x} 
        y={contextMenu.y} 
        item={contextMenu.item} 
        categories={customCategories}
        onclose={() => contextMenu = null}
        onaction={handleAction}
    />
{/if}

<!-- Move to Folder Modal -->
{#if showMoveModal}
    <div 
        class="fixed inset-0 bg-slate-900/60 dark:bg-[#020617]/80 backdrop-blur-md flex items-center justify-center z-[70] p-6"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="bg-white dark:bg-slate-900 rounded-[48px] p-10 w-full max-w-md shadow-2xl border border-white/20 dark:border-slate-800 relative overflow-hidden"
            transition:fly={{ y: 40, duration: 400, easing: quintOut }}
        >
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center space-x-4">
                    <div class="bg-indigo-100 dark:bg-indigo-900/40 p-2.5 rounded-2xl">
                        <Folder class="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div>
                        <h2 class="text-xl font-black text-slate-900 dark:text-white tracking-tight">Move to Folder</h2>
                        <p class="text-slate-400 text-xs font-bold uppercase tracking-widest truncate max-w-[200px]">{moveTargetItem?.name}</p>
                    </div>
                </div>
                <button onclick={() => showMoveModal = false} class="p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-slate-400 transition-all">
                    <X class="w-5 h-5" />
                </button>
            </div>

            <div class="space-y-6">
                <div class="max-h-60 overflow-y-auto custom-scrollbar space-y-2 pr-2">
                    <button 
                        onclick={() => selectedDestinationId = null}
                        class={cn(
                            "w-full flex items-center space-x-3 p-4 rounded-2xl border-2 transition-all group",
                            selectedDestinationId === null 
                                ? "bg-indigo-50 border-indigo-500 dark:bg-indigo-900/20 shadow-inner" 
                                : "bg-slate-50 border-transparent hover:border-slate-200 dark:bg-slate-800/30"
                        )}
                    >
                        <LayoutGrid class="w-5 h-5 text-slate-400 group-hover:text-indigo-600" />
                        <span class="font-bold text-sm text-slate-700 dark:text-slate-200">Main Drive (Root)</span>
                    </button>

                    {#each allFolders as folder}
                        <button 
                            onclick={() => selectedDestinationId = folder.id}
                            class={cn(
                                "w-full flex items-center space-x-3 p-4 rounded-2xl border-2 transition-all group",
                                selectedDestinationId === folder.id 
                                    ? "bg-indigo-50 border-indigo-500 dark:bg-indigo-900/20 shadow-inner" 
                                    : "bg-slate-50 border-transparent hover:border-slate-200 dark:bg-slate-800/30"
                            )}
                        >
                            <Folder class="w-5 h-5 text-amber-500 fill-current" />
                            <span class="font-bold text-sm text-slate-700 dark:text-slate-200">{folder.name}</span>
                        </button>
                    {/each}

                    {#if allFolders.length === 0}
                        <div class="text-center py-8">
                            <p class="text-xs font-bold text-slate-400 uppercase tracking-widest italic">No target folders available</p>
                        </div>
                    {/if}
                </div>

                <button 
                    onclick={confirmMove}
                    class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black rounded-[24px] py-4 shadow-xl shadow-indigo-200 dark:shadow-none transition-all active:scale-[0.98] flex items-center justify-center space-x-2"
                >
                    <span>Confirm Move</span>
                    <ArrowLeft class="w-4 h-4 rotate-180" />
                </button>
            </div>
        </div>
    </div>
{/if}

{#if sharingItem}
    <ShareModal item={sharingItem} onclose={() => sharingItem = null} />
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
