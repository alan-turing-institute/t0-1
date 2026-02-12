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
    <div class="sidebar-tophalf">
        <h1>t0.1 online</h1>
        <div class="sidebar-buttons">
            <span><i>Select conversation:</i></span>
            <div class="conversations">
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
                        <label for={id}>{id}</label>
                        <button
                            class="delete-conversation"
                            onclick={() => deleteConversation(id)}
                            disabled={loading}
                            aria-label="Delete conversation"
                        >
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                {/each}
            </div>
        </div>
    </div>
    <div id="button-wrapper">
        <button
            class="sidebar-bottom {currentId === "__new" ? "bold" : ""}"
            id="newconv"
            onclick={(_e) => newConversation()}>new conversation</button
        >
        <button
            class="sidebar-bottom"
            id="darkmode"
            onclick={(_e) => toggleTheme()}
            >switch to {darkMode ? "light" : "dark"} mode</button
        >
    </div>
</div>

<style>
    div.sidebar {
        height: 100%;
        width: 240px;
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 40px 20px;
        align-items: stretch;
        justify-content: space-between;
        flex: 0 0 auto;
        background-color: var(--sidebar-bg);
    }

    div.sidebar-tophalf {
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
    }

    h1 {
        margin: 0 0 20px 0;
    }

    div.sidebar-buttons {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 20px;
        min-height: 100px;
        max-height: calc(100vh - 270px);
        align-items: stretch;
    }

    div.conversations {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 10px;
        align-items: stretch;
        padding-right: 10px;
        overflow-y: auto;
    }

    div.conversation-manager {
        width: 100%;
        display: flex;
        gap: 10px;
        align-items: center;
        justify-content: space-between;

        label,
        input:disabled + label {
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
            font-size: 0.9em;
            margin: 0 0 0 5px;
            padding: 0;
            cursor: pointer;
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
            margin-bottom: 2px;
            transition: color 0.2s;
        }
        button.delete-conversation:hover {
            color: var(--secondary-fg);
            cursor: pointer;
        }
    }

    div#button-wrapper {
        flex: 0 0 auto;
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 20px;

        button.sidebar-bottom.bold {
            font-weight: bold;
        }

        button.sidebar-bottom {
            font: inherit;
            height: min-content;
            background-color: transparent;
            border: none;
            text-decoration: underline;
            color: var(--foreground);
            cursor: pointer;
            margin: 0 auto;
            transition: font-weight 0.3s;
        }

        button.sidebar-bottom:hover {
            font-weight: bold;
        }
    }
</style>
