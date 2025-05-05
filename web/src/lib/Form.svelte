<script lang="ts">
    interface Props {
        loading: boolean;
        queryLLM: (message: string) => void;
    }

    let { loading, queryLLM }: Props = $props();
    let message: string = $state("");

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSubmit(event);
        }
    }

    function handleSubmit(event: Event) {
        event.preventDefault();
        if (message.trim() === "" || loading) {
            return;
        }
        queryLLM(message);
        message = "";
    }

    let wrapDiv: HTMLDivElement | null = null;
    $effect(() => {
        if (wrapDiv) {
            wrapDiv.dataset.replicatedValue = message;
        }
    });
</script>

<form id="chat" onsubmit={handleSubmit}>
    <div class="grow-wrap" bind:this={wrapDiv}>
        <textarea
            bind:value={message}
            placeholder="Ask me anything..."
            onkeydown={handleKeyDown}
        ></textarea>
    </div>
    <button type="submit" disabled={loading}>Send</button>
</form>

<style>
    form {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    div.grow-wrap {
        width: 100%;
        max-width: 100%;
        display: grid;
    }
    div.grow-wrap::after {
        content: attr(data-replicated-value) " ";
        white-space: pre-wrap;
        visibility: hidden;
    }

    .grow-wrap > textarea {
        resize: none;
    }

    .grow-wrap > textarea,
    .grow-wrap::after {
        width: 100%;
        max-width: 100%;
        max-height: 300px;
        border: 1px solid var(--foreground);
        color: var(--foreground);
        background-color: var(--secondary-bg);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-family: "Fira Code", monospace;
        font-size: inherit;
        grid-area: 1 / 1 / 2 / 2;
        word-break: break-word;
    }

    button {
        font-family: inherit;
        font-size: inherit;
        height: min-content;
        background-color: var(--secondary-bg);
        color: var(--foreground);
        border-radius: 5px;
        padding: 2px 5px;
        border: 1px solid var(--foreground);
    }

    button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
</style>
