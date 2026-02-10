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
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: var(--input-bg);
        border: 1px solid var(--error);
        border-radius: 14px;
        box-shadow: var(--shadow-lg);
        z-index: 100;
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
    }

    p.error-message {
        font-family: "Fira Code", monospace;
        font-size: 0.85em;
        color: var(--error);
    }

    button {
        background: none;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        cursor: pointer;
        font: inherit;
        font-size: 0.85em;
        color: var(--foreground);
        padding: 4px 16px;
        margin: 0 auto;
        transition: background-color 0.15s;
    }
    button:hover {
        background-color: var(--sidebar-hover);
    }
</style>
