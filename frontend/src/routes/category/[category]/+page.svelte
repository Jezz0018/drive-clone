<script lang="ts">
    import { page } from '$app/state';
    import Header from '$lib/components/Header.svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import FileExplorer from '$lib/components/FileExplorer.svelte';

    let category = $derived(page.params.category);
    let title = $derived(category.charAt(0).toUpperCase() + category.slice(1));
    let explorer = $state<any>();
</script>

<div class="h-screen flex flex-col">
    <Header onSearch={(q: string) => explorer?.handleSearch(q)} />
    <div class="flex-1 flex overflow-hidden">
        <Sidebar activeView={`cat-${category}`} />
        <FileExplorer bind:this={explorer} title={`${title} Files`} {category} />
    </div>
</div>
