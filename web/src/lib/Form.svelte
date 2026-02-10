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

<div class="form-area">
    <Demographics {changeDemographics} />
    <form id="chat" onsubmit={handleSubmit}>
        <div class="input-wrapper">
            <div class="grow-wrap" bind:this={wrapDiv}>
                <textarea
                    bind:value={message}
                    placeholder="Ask me anything..."
                    onkeydown={handleKeyDown}
                ></textarea>
            </div>
            <button type="submit" disabled={loading} aria-label="Send">
                <i class="fa-solid fa-arrow-up"></i>
            </button>
        </div>
    </form>
</div>

<style>
    .form-area {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    form {
        width: 100%;
    }

    .input-wrapper {
        display: flex;
        align-items: flex-end;
        gap: 0;
        background-color: var(--input-bg);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        box-shadow: var(--shadow-md);
        padding: 4px 6px 4px 4px;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .input-wrapper:focus-within {
        border-color: var(--accent);
        box-shadow: 0 0 0 2px var(--accent-light), var(--shadow-md);
    }

    div.grow-wrap {
        flex: 1 1 auto;
        display: grid;
        min-width: 0;
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
        max-height: 200px;
        border: none;
        color: var(--foreground);
        background: transparent;
        border-radius: 20px;
        padding: 10px 14px;
        font-family: inherit;
        font-size: inherit;
        grid-area: 1 / 1 / 2 / 2;
        word-break: break-word;
        outline: none;
    }

    button {
        flex: 0 0 auto;
        font-family: inherit;
        font-size: 0.9em;
        height: 36px;
        width: 36px;
        background-color: var(--accent);
        color: white;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.15s, opacity 0.15s;
    }

    button:hover {
        opacity: 0.85;
    }

    button:disabled {
        background-color: var(--button-disabled-bg);
        color: var(--button-disabled-fg);
        cursor: not-allowed;
        opacity: 1;
    }
</style>
