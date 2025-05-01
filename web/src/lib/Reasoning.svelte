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
            {expand ? "⏷" : "⏵"}
        </button>
        <button {onclick}>
            {expand ? "Hide" : "Show"} reasoning
        </button>
        {#if expand}
            <div></div>
            <div class="reasoning" transition:slide>
                {@html reasoning}
            </div>
        {/if}
    </div>
{/if}

<style>
    div.wrapper {
        display: grid;
        grid-template-columns: auto 1fr;
        grid-column-gap: 10px;
    }
    button {
        background-color: transparent;
        border: none;
        cursor: pointer;
        font: inherit;
        color: var(--secondary-fg);
        width: max-content;
        padding: 0;
        margin: 0;
        font-size: 0.8em;
    }

    div.reasoning {
        margin: 0;
        padding: 10px 0 0 0;
        font-size: 0.8em;
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
