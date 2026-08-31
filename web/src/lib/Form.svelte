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
    <button type="submit" disabled={loading} aria-label="Send">
        <i class="fa-solid fa-paper-plane"></i>
    </button>
</form>

<style>
    form {
        width: 100%;
        display: grid;
        grid-template-columns: 1fr max-content;
        gap: 0 10px;
        align-items: end;
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
        border: 1.5px solid var(--border-color);
        color: var(--foreground);
        background-color: var(--secondary-bg);
        border-radius: 20px;
        padding: 10px 16px;
        font-family: inherit;
        font-size: inherit;
        line-height: 1.5;
        grid-area: 1 / 1 / 2 / 2;
        word-break: break-word;
        transition:
            border-color 0.15s ease,
            box-shadow 0.15s ease;
    }

    .grow-wrap > textarea:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--focus-ring);
    }

    button {
        font-family: inherit;
        font-size: 1.1em;
        height: 40px;
        width: 40px;
        background-color: var(--accent);
        color: var(--accent-fg);
        border-radius: 50%;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 4px;
        transition:
            background-color 0.15s ease,
            transform 0.1s ease;
    }

    button:hover {
        background-color: var(--accent-hover);
        transform: scale(1.05);
    }

    button:active {
        transform: scale(0.95);
    }

    button:disabled {
        background-color: var(--button-disabled-bg);
        color: var(--button-disabled-fg);
        cursor: not-allowed;
        transform: none;
    }

    @media (max-width: 768px) {
        button {
            height: 44px;
            width: 44px;
        }
    }
</style>
