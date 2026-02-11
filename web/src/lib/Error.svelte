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
        background-color: var(--error-bg);
        border: 1px solid var(--error-border);
        border-radius: 12px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        z-index: 4;
        text-align: center;
        padding: 16px 24px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        max-width: 480px;
    }

    div#error p {
        margin: 0;
        padding: 0;
        color: var(--error-fg);
    }

    p.error-message {
        font-size: 0.9em;
        word-break: break-word;
    }

    button {
        background-color: transparent;
        border: none;
        cursor: pointer;
        text-decoration: underline;
        font: inherit;
        font-weight: 500;
        color: var(--error-fg);
        padding: 4px;
        transition: opacity 0.15s ease;
    }
    button:hover {
        opacity: 0.7;
    }
</style>
