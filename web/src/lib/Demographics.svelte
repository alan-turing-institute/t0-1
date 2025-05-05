<script lang="ts">
    import { slide } from "svelte/transition";
    import { type Demographics } from "./types";

    interface Props {
        changeDemographics: (demographics: Demographics) => void;
    }
    let { changeDemographics }: Props = $props();

    function onkeydown(event: KeyboardEvent) {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    }

    let showForm = $state(false);
    let demographics: Demographics = $state({
        name: "",
        age: 0,
    });
</script>

<div id="demographics-wrapper">
    {#if showForm}
        <div id="demographics" transition:slide>
            name:
            <input
                type="text"
                bind:value={demographics.name}
                oninput={() => changeDemographics(demographics)}
                {onkeydown}
            />
            age:
            <input
                type="number"
                bind:value={demographics.age}
                oninput={() => changeDemographics(demographics)}
                {onkeydown}
            />
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
        border-radius: 10px;
        border: 1px solid var(--foreground);
    }

    button#toggle {
        background-color: transparent;
        border: none;
        cursor: pointer;
        font: inherit;
        color: var(--secondary-fg);
        width: 100%;
        padding: 0;
        margin: 0;
        font-size: 0.8em;
    }
</style>
