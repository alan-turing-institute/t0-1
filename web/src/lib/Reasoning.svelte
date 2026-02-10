<script lang="ts">
    import { slide } from "svelte/transition";

    let { reasoning }: { reasoning: string | null } = $props();

    let expand: boolean = $state(false);

    function onclick() {
        expand = !expand;
    }
</script>

{#if reasoning}
    <button class="reasoning-toggle" {onclick}>
        <i class="fa-solid {expand ? 'fa-chevron-down' : 'fa-chevron-right'}"></i>
        {expand ? "Hide" : "Show"} reasoning
    </button>
    {#if expand}
        <div class="reasoning" transition:slide>
            {@html reasoning}
        </div>
    {/if}
{/if}

<style>
    .reasoning-toggle {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: none;
        border: none;
        cursor: pointer;
        font: inherit;
        color: var(--secondary-fg);
        padding: 4px 8px;
        margin: 0;
        font-size: 0.8em;
        border-radius: 6px;
        transition: color 0.15s, background-color 0.15s;
    }
    .reasoning-toggle:hover {
        color: var(--foreground);
        background-color: var(--sidebar-hover);
    }

    .reasoning-toggle i {
        font-size: 0.7em;
    }

    div.reasoning {
        margin: 0;
        padding: 10px 0 0 0;
        font-size: 0.8em;
        color: var(--secondary-fg);
        border-left: 2px solid var(--border-color);
        padding-left: 12px;
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
