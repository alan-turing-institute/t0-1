<script lang="ts">
    interface Props {
        allIds: Array<string>;
        changeId: (id: string) => void;
        newConversation: () => void;
        deleteConversation: (id: string) => void;
        darkMode: boolean;
        toggleTheme: () => void;
    }

    let {
        allIds,
        changeId,
        newConversation,
        deleteConversation,
        darkMode,
        toggleTheme,
    }: Props = $props();
</script>

<div class="sidebar">
    <div>
        <h1>t0 online</h1>
        <div class="sidebar-buttons">
            <div class="conversations">
                <span>Select conversation:</span>
                {#each allIds as id}
                    <div class="conversation-manager">
                        <label for={id}>{id.slice(0, 8)}</label>
                        <input
                            {id}
                            type="radio"
                            value={id}
                            name="conversation"
                            onchange={() => changeId(id)}
                            hidden
                        />
                        <button
                            class="delete-conversation"
                            onclick={() => deleteConversation(id)}
                        >
                            x
                        </button>
                    </div>
                {/each}
            </div>
            <button class="new-conversation" onclick={newConversation}
                >New conversation</button
            >
        </div>
    </div>
    <button onclick={(_e) => toggleTheme()}
        >switch to {darkMode ? "light" : "dark"} mode</button
    >
</div>

<style>
    div.sidebar {
        height: 100%;
        width: max-content;
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 40px 20px;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: auto;
        flex: 0 0 auto;
        background-color: var(--sidebar-bg);
    }

    h1 {
        margin: 0 0 20px 0;
    }

    div.sidebar-buttons {
        display: flex;
        flex-direction: column;
        gap: 20px;
        align-items: stretch;
    }

    div.conversations {
        display: flex;
        flex-direction: column;
        gap: 10px;
        align-items: stretch;
    }

    div.conversation-manager {
        display: flex;
        gap: 10px;
        justify-content: space-between;
        align-items: center;

        label {
            font-family: "Fira Code", monospace;
            margin: 0;
            padding: 0;
            background-color: var(--secondary-bg);
            cursor: pointer;
            flex: 1 1 auto;
        }
        label:hover {
            background-color: var(--hover-bg);
        }

        button.delete-conversation {
            flex: 0 0 auto;
        }
    }

    button {
        font: inherit;
        height: min-content;
        background-color: transparent;
        border: none;
        text-decoration: underline;
        color: var(--foreground);
        cursor: pointer;
        text-align: left;
    }
</style>
