<script lang="ts">
    import Header from '$lib/components/Header.svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import FileExplorer from '$lib/components/FileExplorer.svelte';

    let explorer = $state<any>();
</script>

<div class="h-screen flex flex-col">
    <Header onSearch={(q: string) => explorer?.handleSearch(q)} />
    <div class="flex-1 flex overflow-hidden">
        <Sidebar activeView="starred" />
        <FileExplorer bind:this={explorer} title="Favorites" isStarred={true} />
    </div>
</div>
