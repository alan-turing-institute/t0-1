<script lang="ts">
    interface Props {
        allIds: Array<string>;
        currentId: string;
        changeId: (id: string) => void;
        newConversation: () => void;
        darkMode: boolean;
        toggleTheme: () => void;
    }

    let {
        allIds,
        currentId,
        changeId,
        newConversation,
        darkMode,
        toggleTheme,
    }: Props = $props();

    function handleSelectChange(event: Event) {
        const target = event.target as HTMLSelectElement;
        if (target.value === "new") {
            newConversation();
        } else {
            changeId(target.value);
        }
    }
</script>

<div class="header">
    <h1>t0 online (but really gpt-4o)</h1>
    <select bind:value={currentId} onchange={handleSelectChange}>
        {#each allIds as id}
            <option value={id}>{id}</option>
        {/each}
        <option value="new">new conversation</option>
    </select>
    <button onclick={(_e) => toggleTheme()}
        >switch to {darkMode ? "light" : "dark"} mode</button
    >
</div>

<style>
    div.header {
        display: flex;
        gap: 20px;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: auto;
    }

    h1 {
        margin: 0;
        padding-left: 10px;
    }

    button {
        height: min-content;
        background-color: transparent;
        border: none;
        font: 0.8em;
        text-decoration: underline;
        color: var(--foreground);
    }
</style>
