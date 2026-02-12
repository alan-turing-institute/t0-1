<script lang="ts">
    import { fade } from "svelte/transition";

    let { error }: { error: string | null } = $props();
</script>

{#if error}
    <div id="error" transition:fade>
        <p>Oops! Something went wrong:</p>
        <p class="error-message">{error}</p>
        <button
            onclick={() => {
                error = null;
            }}>OK</button
        >
    </div>
{/if}

<style>
    div#error {
        position: fixed;
        top: 100px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #fceafb;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        z-index: 4;
        text-align: center;
        padding: 10px 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    div#error p {
        margin: 0;
        padding: 0;
    }

    p.error-message {
        font-family: "Fira Code", monospace;
    }

    button {
        background-color: transparent;
        border: none;
        cursor: pointer;
        text-decoration: underline;
        font: inherit;
        color: #a5354f;
    }
</style>
