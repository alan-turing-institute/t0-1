<script lang="ts">
    import { type ChatEntry } from "./types";

    interface Props {
        history: Array<ChatEntry>;
    }

    let { history }: Props = $props();
    let chatLogDiv: HTMLDivElement | null = null;

    export function scrollToBottom() {
        if (chatLogDiv) {
            setTimeout(() => {
                chatLogDiv.scrollTop = chatLogDiv.scrollHeight;
            }, 100);
        }
    }
</script>

<div class="chatlog" bind:this={chatLogDiv}>
    {#each history as entry}
        <div class={entry.role}>
            {entry.content}
        </div>
    {/each}
</div>

<style>
    div.chatlog {
        width: 100%;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 5px;
        padding-bottom: 20px;
        scroll-behavior: smooth;
    }

    div.human,
    div.ai {
        width: max-content;
        max-width: 60%;
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid black;
    }

    div.human {
        text-align: right;
        margin-left: auto;
    }

    div.ai {
        text-align: left;
        margin-right: auto;
    }
</style>
