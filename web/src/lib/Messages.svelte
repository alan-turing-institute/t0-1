<script lang="ts">
    import { type ChatEntry, type AIChatEntry, makeAIEntry } from "./types";
    import Loading from "./Loading.svelte";
    import Reasoning from "./Reasoning.svelte";

    interface Props {
        history: Array<ChatEntry>;
        loading: boolean;
        nextMessage: string;
    }

    let { history, loading, nextMessage }: Props = $props();

    let nextMessageParsed: AIChatEntry[] = $derived(
        nextMessage === "" ? [] : [makeAIEntry(nextMessage)],
    );
    let nextMessageHasContent: boolean = $derived(
        nextMessageParsed.length > 0 &&
            nextMessageParsed[0].content.trim() !== "",
    );
    let historyCombined = $derived([...history, ...nextMessageParsed]);

    // $effect(() => {
    //     console.log(nextMessage);
    // });

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
    }

    function scroll(node: HTMLDivElement) {
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
    {#each historyCombined as entry}
        <div class={entry.role} use:scroll>
            {#if entry.role === "ai"}
                {#if entry.content !== ""}
                    {@html entry.content}
                {/if}
                {#if nextMessageHasContent || !loading}
                    <Reasoning reasoning={entry.reasoning} />
                {/if}
            {:else if entry.role === "human"}
                {@html entry.content}
            {:else if entry.role === "tool"}
                    <p>Looked up the following sources:</p>
                    <ul>
                        {#each entry.sources as source}
                            <li>
                                <a
                                    href="https://www.nhs.uk/conditions/{source}"
                                    target="_blank">{source}</a
                                >
                            </li>
                        {/each}
                    </ul>
            {/if}
        </div>
    {/each}
</div>
{#if loading && !nextMessageHasContent}
    <Loading />
{/if}

<style>
    div.chatlog {
        width: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 30px;
        margin: auto 0 20px 0;
        padding: 0px 10px;
        scroll-behavior: smooth;
    }
    div.chatlog > :last-child {
        margin-bottom: 100vh;
    }

    div.tool {
        font-size: 0.8em;
        color: var(--secondary-fg);

        a {
            color: var(--secondary-fg);
        }
        a:hover,
        a:active,
        a:focus {
            color: var(--foreground);
        }

        p {
            margin: 0;
            padding: 0;
        }
        ul {
            margin: 0;
            padding-left: 20px;
        }
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
