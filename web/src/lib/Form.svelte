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
</script>

<form id="chat" onsubmit={handleSubmit}>
    <textarea
        bind:value={message}
        placeholder="Your message here..."
        onkeydown={handleKeyDown}
    ></textarea>
    <button type="submit" disabled={disableForm}>Send</button>
</form>

<style>
    form {
        border: 1px solid blue;
        width: 100%;
        display: flex;
        gap: 10px;
    }

    textarea,
    button {
        font-size: inherit;
    }

    textarea {
        width: 100%;
        font-family: "Fira Mono", monospace;
    }

    button {
        font-family: inherit;
    }

    button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
</style>
