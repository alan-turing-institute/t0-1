<script lang="ts">
    import Demographics from "./Demographics.svelte";
    import { type Demographics as DemographicsType } from "./types";

    interface Props {
        loading: boolean;
        queryLLM: (message: string) => void;
        changeDemographics: (demographics: DemographicsType) => void;
    }

    let { loading, queryLLM, changeDemographics }: Props = $props();
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
    <Demographics {changeDemographics} />
    <div class="grow-wrap" bind:this={wrapDiv}>
        <textarea
            bind:value={message}
            placeholder="Ask me anything..."
            onkeydown={handleKeyDown}
        ></textarea>
    </div>
    <button type="submit" disabled={loading}>
        <i class="fa-solid fa-paper-plane"></i>
    </button>
</form>

<style>
    form {
        width: 100%;
        display: grid;
        grid-template-columns: 1fr max-content;
        gap: 0 10px;
        align-items: center;
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
        font-size: 1.5em;
        height: 40px;
        width: 40px;
        background-color: var(--secondary-bg);
        color: var(--foreground);
        border-radius: 50%;
        padding-right: 6px;
        border: 1px solid var(--foreground);
        cursor: pointer;
    }

    button:active {
        background-color: var(--button-disabled-bg);
        color: var(--button-disabled-fg);
    }

    button:disabled {
        background-color: var(--button-disabled-bg);
        color: var(--button-disabled-fg);
        cursor: not-allowed;
    }
</style>
