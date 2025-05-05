<script lang="ts">
    import { slide } from "svelte/transition";

    let demographics_string: string = $state("");

    let showForm = $state(false);
</script>

<div id="demographics-wrapper">
    {#if showForm}
        <div id="demographics" transition:slide>
            <input type="text" bind:value={demographics_string} />
        </div>
    {/if}
    <div id="toggle">
        <button id="toggle" onclick={() => (showForm = !showForm)}>
            {showForm ? "⏷ hide" : "⏶ show"} demographics
        </button>
    </div>
</div>
<div></div>

<style>
    div#demographics-wrapper {
        margin: 0 10px;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid var(--foreground);
    }

    button#toggle {
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
</style>
