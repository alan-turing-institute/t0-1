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

    // Controls whether the chat log should auto-scroll to the newest entry when it's added
    let chatLogDiv: HTMLDivElement | null = null;

    function scroll(node: HTMLDivElement) {
        // find the last human message and scroll to the top of that -
        // this mimics chatgpt behaviour
        const messageNodes = node.parentElement.children;
        const lastHumanMessage = Array.from(messageNodes)
            .reverse()
            .find((child) => {
                return child.classList.contains("human");
            });
        if (!node.classList.contains("human")) {
            // disable smooth scrolling
            chatLogDiv!.style.scrollBehavior = "auto";
        }
        lastHumanMessage.scrollIntoView(true);
        chatLogDiv!.style.scrollBehavior = "smooth";
    }
</script>

<div class="chatlog" bind:this={chatLogDiv}>
    {#each historyCombined as entry}
        {#if entry.role === "ai"}
            <div class="ai-wrapper" use:scroll>
                <div class="avatar">t0</div>
                <div class="ai">
                    {#if entry.content !== ""}
                        {@html entry.content}
                    {/if}
                    {#if nextMessageHasContent || !loading}
                        <Reasoning reasoning={entry.reasoning} />
                    {/if}
                </div>
            </div>
        {:else if entry.role === "human"}
            <div class="human" use:scroll>
                {@html entry.content}
            </div>
        {:else if entry.role === "tool"}
            <div class="tool" use:scroll>
                <span class="tool-label">Sources:</span>
                {#each entry.sources as source}
                    <a
                        class="source-chip"
                        href="https://www.nhs.uk/conditions/{source}"
                        target="_blank">{source}</a
                    >
                {/each}
            </div>
        {/if}
    {/each}
</div>
<Loading show={loading && !nextMessageHasContent} />

<style>
    div.chatlog {
        width: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 24px;
        margin: auto 0 16px 0;
        padding: 0px 4px;
        scroll-behavior: smooth;
    }

    div.chatlog > :last-child {
        margin-bottom: 100vh;
    }

    .ai-wrapper {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        width: 100%;
    }

    .avatar {
        flex: 0 0 auto;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--linear-gradient-start), var(--linear-gradient-end));
        color: white;
        font-size: 0.65em;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 2px;
    }

    div.tool {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
        padding-left: 44px;
    }

    .tool-label {
        font-size: 0.8em;
        color: var(--secondary-fg);
    }

    .source-chip {
        font-size: 0.75em;
        padding: 3px 10px;
        border-radius: 20px;
        background-color: var(--accent-light);
        color: var(--accent);
        text-decoration: none;
        transition: background-color 0.15s;
    }
    .source-chip:hover {
        background-color: var(--sidebar-hover);
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
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    div.human {
        max-width: 70%;
        width: max-content;
        background-color: var(--user-message-bg);
        border-radius: 20px;
        padding: 12px 18px;
        margin-left: auto;
    }

    div.ai {
        width: 100%;
        text-align: left;
        min-width: 0;
    }
</style>
