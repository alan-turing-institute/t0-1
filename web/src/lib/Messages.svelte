<script lang="ts">
    import { type ChatEntry } from "./types";
    import Loading from "./Loading.svelte";
    import Reasoning from "./Reasoning.svelte";
    // import Typewriter from "svelte-typewriter";

    interface Props {
        history: Array<ChatEntry>;
        loading: boolean;
    }

    let { history, loading }: Props = $props();

    // Controls whether the chat log should auto-scroll to the newest entry when it's added
    let autoScroll: boolean = true;
    let chatLogDiv: HTMLDivElement | null = null;

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
            // find the last human message and scroll to the top of that -
            // this mimics chatgpt behaviour
            const messageNodes = node.parentElement.children;
            const lastHumanMessage = Array.from(messageNodes)
                .reverse()
                .find((child) => {
                    return child.classList.contains("human");
                });
            lastHumanMessage.scrollIntoView(true);
        }
    }
</script>

<div class="chatlog" onscroll={setAutoScroll} bind:this={chatLogDiv}>
    {#each history as entry}
        <div class={entry.role} use:scroll>
            {#if entry.role === "ai"}
                {@html entry.content}
                <!-- Disabling typewriter for now as it messes with scroll -->
                <!-- <Typewriter cursor={false} mode="cascade" interval="8" -->
                <!--     >{@html entry.content}</Typewriter -->
                <!-- > -->
                <Reasoning reasoning={entry.reasoning} />
            {:else}
                {@html entry.content}
            {/if}
        </div>
    {/each}
    {#if loading}
        <Loading />
    {/if}
</div>

<style>
    div.chatlog {
        width: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 30px;
        margin: auto 0 10px 0;
        padding: 0px 10px;
        scroll-behavior: smooth;
    }

    div.human :global,
    div.ai :global,
    div.loading :global {
        p {
            margin: 0;
            padding: 0;
        }

        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            margin: 10px 0 5px 0;
        }

        ul,
        ol {
            margin: 0;
            padding-left: 1.5em;
        }

        ul ul,
        ul ol,
        ol ul,
        ol ol {
            /* Nested lists */
            margin-top: 5px;
        }

        li + li {
            margin-top: 5px;
        }
    }

    div.human,
    div.ai {
        width: max-content;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    div.human {
        max-width: 60%;
        background-color: var(--user-message-bg);
        border-radius: 15px;
        padding: 10px 15px;
        margin-left: auto;
    }

    div.ai {
        width: 100%;
        text-align: left;
        margin-right: auto;
    }
</style>
