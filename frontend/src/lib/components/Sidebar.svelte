<script lang="ts">
    import { 
        Home, 
        Folder, 
        Star, 
        Clock, 
        Trash2, 
        HardDrive,
        Plus
    } from 'lucide-svelte';
    import { page } from '$app/stores';

    export let activeView = 'my-drive';

    const menuItems = [
        { id: 'my-drive', label: 'My Drive', icon: HardDrive, path: '/' },
        { id: 'recent', label: 'Recent', icon: Clock, path: '/recent' },
        { id: 'starred', label: 'Starred', icon: Star, path: '/starred' },
        { id: 'trash', label: 'Trash', icon: Trash2, path: '/trash' },
    ];
</script>

<aside class="w-64 bg-gray-50 h-screen flex flex-col border-r border-gray-200">
    <div class="p-4">
        <button class="flex items-center space-x-2 bg-white border border-gray-200 rounded-full px-4 py-3 shadow-sm hover:shadow-md transition-shadow">
            <Plus class="w-6 h-6 text-blue-600" />
            <span class="font-medium">New</span>
        </button>
    </div>

    <nav class="flex-1 px-2 space-y-1">
        {#each menuItems as item}
            <a 
                href={item.path}
                class="flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors {activeView === item.id ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-200 text-gray-700'}"
            >
                <svelte:component this={item.icon} class="w-5 h-5" />
                <span>{item.label}</span>
            </a>
        {/each}
    </nav>

    <div class="p-4 border-t border-gray-200">
        <div class="text-sm text-gray-500 mb-2">Storage</div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 mb-2">
            <div class="bg-blue-600 h-1.5 rounded-full" style="width: 15%"></div>
        </div>
        <div class="text-xs text-gray-500">1.2 GB of 15 GB used</div>
    </div>
</aside>
