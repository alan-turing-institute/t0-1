<script lang="ts">
    import { type ChatEntry } from "./types";

    interface Props {
        history: Array<ChatEntry>;
    }

    let { history }: Props = $props();

    // Controls whether the chat log should auto-scroll to the newest entry when it's added
    let autoScroll: boolean = true;

    function setAutoScroll(event: Event) {
        const target = event.target as HTMLDivElement;
        const scrollTop = target.scrollTop;
        const scrollHeight = target.scrollHeight;
        const clientHeight = target.clientHeight;

        // If the user has scrolled up, disable auto-scroll
        if (scrollTop + clientHeight < scrollHeight) {
            autoScroll = false;
        } else {
            autoScroll = true;
        }
    }

    function scroll(node: HTMLDivElement) {
        // If it's a new message from the user, force the scroll
        // to happen.
        if (node.classList.contains("human")) {
            autoScroll = true;
        }
        if (autoScroll) {
            node.scrollIntoView(true);
        }
    }
</script>

<div class="chatlog" onscroll={setAutoScroll}>
    {#each history as entry}
        <div class={entry.role} use:scroll>
            {@html entry.content}
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
