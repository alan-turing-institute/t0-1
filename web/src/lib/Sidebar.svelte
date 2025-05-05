<script lang="ts">
    import { slide } from "svelte/transition";

    interface Props {
        currentId: string;
        loading: boolean;
        allIds: Array<string>;
        changeId: (id: string) => void;
        newConversation: () => void;
        deleteConversation: (id: string) => void;
        darkMode: boolean;
        toggleTheme: () => void;
    }

    let {
        currentId,
        loading,
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
                <span><i>Select conversation:</i></span>
                {#each allIds as id}
                    <div class="conversation-manager" transition:slide>
                        <input
                            {id}
                            type="radio"
                            value={id}
                            name="conversation"
                            onchange={() => changeId(id)}
                            bind:group={currentId}
                            disabled={loading}
                            hidden
                        />
                        <label for={id}>{id.slice(0, 8)}</label>
                        <button
                            class="delete-conversation"
                            onclick={() => deleteConversation(id)}
                            disabled={loading}
                        >
                            (×)
                        </button>
                    </div>
                {/each}
                <div class="conversation-manager">
                    <input
                        id="new"
                        type="radio"
                        value="new"
                        name="conversation"
                        onchange={() => newConversation()}
                        bind:group={currentId}
                        disabled={loading}
                        hidden
                    />
                    <label for={"new"}>(new)</label>
                </div>
            </div>
        </div>
    </div>
    <button id="darkmode" onclick={(_e) => toggleTheme()}
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

        label, input:disabled + label {
            font-family: "Fira Code", monospace;
            margin: 0 0 0 10px;
            padding: 0;
            cursor: pointer;
            flex: 1 1 auto;
            transition: background-size 0.3s;
            background: linear-gradient(
                    to right,
                    rgba(0, 0, 0, 0),
                    rgba(0, 0, 0, 0)
                ),
                linear-gradient(
                    to right,
                    var(--linear-gradient-start),
                    var(--linear-gradient-end)
                );
            background-size:
                100% 2px,
                0 2px;
            background-position:
                100% 100%,
                0 100%;
            background-repeat: no-repeat;
        }
        input:disabled + label {
            cursor: normal;
        }
        label:hover,
        label:active {
            background-size:
                0 2px,
                100% 2px;
        }

        input:checked + label {
            font-weight: bold;
            transition:
                font-weight 0.3s,
                background-size 0.3s;
        }

        button.delete-conversation {
            flex: 0 0 auto;
            background-color: transparent;
            color: var(--foreground);
            text-decoration: none;
            border: none;
        }
        button.delete-conversation:hover {
            font-weight: bold;
            cursor: pointer;
        }
    }

    button#darkmode {
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
