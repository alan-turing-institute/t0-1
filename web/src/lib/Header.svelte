<script lang="ts">
    interface Props {
        allIds: Array<string>;
        currentId: string;
        changeId: (id: string) => void;
        newConversation: () => void;
        deleteCurrentConversation: () => void;
        darkMode: boolean;
        toggleTheme: () => void;
    }

    let {
        allIds,
        currentId,
        changeId,
        newConversation,
        deleteCurrentConversation,
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
    <div class="header-buttons">
        <div>
            current conversation
            <select bind:value={currentId} onchange={handleSelectChange}>
                {#each allIds as id}
                    <option value={id}>{id.slice(0, 5)}</option>
                {/each}
                <option value="new">(new)</option>
            </select>
        </div>
        <button onclick={(_e) => deleteCurrentConversation()}
            >delete conversation</button
        >
        <button onclick={(_e) => toggleTheme()}
            >switch to {darkMode ? "light" : "dark"} mode</button
        >
    </div>
</div>

<style>
    div.header {
        display: flex;
        gap: 20px;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: auto;
    }

    h1 {
        margin: 0;
        padding-left: 10px;
    }

    div.header-buttons {
        font-size: 0.8em;
        display: flex;
        flex-direction: column;
        gap: 5px;
        align-items: flex-end;
    }

    select {
        font: inherit;
        color: var(--foreground);
        background-color: transparent;
        border-radius: 5px;
        border: 1px solid var(--foreground);
    }

    button {
        font: inherit;
        height: min-content;
        background-color: transparent;
        border: none;
        text-decoration: underline;
        color: var(--foreground);
        cursor: pointer;
    }
</style>
