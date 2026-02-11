<script lang="ts">
    import { slide } from "svelte/transition";

    let { reasoning }: { reasoning: string | null } = $props();

    let expand: boolean = $state(false);

    function onclick() {
        expand = !expand;
    }
</script>

{#if reasoning}
    <div class="wrapper">
        <button {onclick}>
            {expand ? "▾ Hide" : "▸ Show"} reasoning
        </button>
        {#if expand}
            <div class="reasoning" transition:slide>
                {@html reasoning}
            </div>
        {/if}
    </div>
{/if}

<style>
    div.wrapper {
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    button {
        background-color: transparent;
        border: none;
        cursor: pointer;
        font: inherit;
        color: var(--reasoning-fg);
        width: max-content;
        padding: 4px 0;
        margin: 0;
        font-size: 0.8em;
        font-weight: 500;
        transition: color 0.15s ease;
    }
    button:hover {
        color: var(--accent);
    }

    div.reasoning {
        margin: 8px 0 0 0;
        padding: 12px 16px;
        font-size: 0.8em;
        color: var(--reasoning-fg);
        background-color: var(--reasoning-bg);
        border-left: 3px solid var(--reasoning-border);
        border-radius: 0 8px 8px 0;
    }

    div.reasoning :global {
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
    }
</style>
