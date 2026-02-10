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
<Loading show={loading && !nextMessageHasContent} />

<style>
    div.chatlog {
        width: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 24px;
        margin: auto 0 20px 0;
        padding: 0px 4px;
        scroll-behavior: smooth;
    }

    div.chatlog > :last-child {
        margin-bottom: 100vh;
    }

    div.tool {
        font-size: 0.8em;
        color: var(--secondary-fg);

        a {
            color: var(--accent);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition:
                color 0.15s ease,
                border-color 0.15s ease;
        }
        a:hover,
        a:active,
        a:focus {
            color: var(--accent-hover);
            border-bottom-color: var(--accent);
        }

        p {
            margin: 0;
            padding: 0;
        }
        ul {
            margin: 4px 0 0 0;
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

        a {
            color: var(--accent);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition:
                color 0.15s ease,
                border-color 0.15s ease;
        }
        a:hover {
            color: var(--accent-hover);
            border-bottom-color: var(--accent);
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
        max-width: 70%;
        background-color: var(--user-message-bg);
        border-radius: 18px 18px 4px 18px;
        padding: 10px 16px;
        margin-left: auto;
        box-shadow: 0 1px 3px var(--user-message-shadow);
    }

    div.ai {
        width: 100%;
        text-align: left;
        margin-right: auto;
        border-radius: 18px 18px 18px 4px;
    }
</style>
