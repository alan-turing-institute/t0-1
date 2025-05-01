<script lang="ts">
    import { type ChatEntry } from "./types";

    interface Props {
        history: Array<ChatEntry>;
        loading: boolean;
    }

    let { history, loading }: Props = $props();

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
        console.log("Auto-scroll:", autoScroll);
    }

    function scroll(node: HTMLDivElement) {
        console.log("scrolling", node.classList);
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
    {#if loading}
        <div class="loading" use:scroll></div>
    {/if}
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
    div.ai,
    div.loading {
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

    div.ai,
    div.loading {
        text-align: left;
        margin-right: auto;
    }

    div.loading::after {
        content: "";
        display: inline-block;
        animation: dots 1.5s steps(4, start) infinite;
        white-space: pre;
    }
    @keyframes dots {
        0% {
            content: "";
        }
        5% {
            content: ".";
        }
        10% {
            content: "..";
        }
        15% {
            content: "...";
        }
        100% {
            content: "";
        }
    }
</style>
