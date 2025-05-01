<script lang="ts">
    interface Props {
        disableForm: boolean;
        queryLLM: (message: string) => void;
    }

    let { disableForm, queryLLM }: Props = $props();
    let message: string = $state("");

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSubmit(event);
        }
    }

    function handleSubmit(event: Event) {
        event.preventDefault();
        if (message.trim() === "" || disableForm) {
            return;
        }
        queryLLM(message);
        message = "";
    }

    let wrapDiv: HTMLDivElement | null = null;
    function handleInput(_event: Event) {
        if (wrapDiv) {
            wrapDiv.dataset.replicatedValue = message;
        }
    }
</script>

<form id="chat" onsubmit={handleSubmit}>
    <div class="grow-wrap" bind:this={wrapDiv}>
        <textarea
            bind:value={message}
            placeholder="Your message here..."
            onkeydown={handleKeyDown}
            oninput={handleInput}
        ></textarea>
    </div>
    <button type="submit" disabled={disableForm}>Send</button>
</form>

<style>
    form {
        border: 1px solid blue;
        width: 100%;
        display: flex;
        gap: 10px;
    }

    div.grow-wrap {
        width: 100%;
        display: grid;
    }
    div.grow-wrap::after {
        content: attr(data-replicated-value) " ";
        white-space: pre-wrap;
        visibility: hidden;
    }

    textarea,
    button {
        font-size: inherit;
    }

    .grow-wrap > textarea {
        resize: none;
    }

    .grow-wrap > textarea,
    .grow-wrap::after {
        width: 100%;
        max-height: 300px;
        border: 1px solid black;
        padding: 0.5rem;
        font-family: "Fira Code", monospace;
        grid-area: 1 / 1 / 2 / 2;
    }

    button {
        font-family: inherit;
    }

    button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
</style>
