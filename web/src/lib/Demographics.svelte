<script lang="ts">
    import { slide } from "svelte/transition";
    import { type Demographics, emptyDemographics } from "./types";

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
    let demographics: Demographics = $state(emptyDemographics);

    function onclick(event: MouseEvent) {
        event.preventDefault();
        showForm = !showForm;
    }
</script>

<div id="demographics-wrapper">
    {#if showForm}
        <div id="demographics" transition:slide>
            age
            <input
                type="number"
                bind:value={demographics.age}
                oninput={() => changeDemographics(demographics)}
                {onkeydown}
            />
            sex
            <select
                bind:value={demographics.sex}
                onchange={() => changeDemographics(demographics)}
                {onkeydown}
            >
                <option value="unspecified">(select)</option>
                <option value="female">female</option>
                <option value="male">male</option>
            </select>
            occupation
            <input
                type="text"
                bind:value={demographics.occupation}
                oninput={() => changeDemographics(demographics)}
                {onkeydown}
            />
            support system
            <input
                type="text"
                bind:value={demographics.supportSystem}
                oninput={() => changeDemographics(demographics)}
                {onkeydown}
            />
            medical history
            <input
                type="text"
                bind:value={demographics.medicalHistory}
                oninput={() => changeDemographics(demographics)}
                {onkeydown}
            />
        </div>
    {/if}
    <div id="toggle">
        <button id="toggle" {onclick}>
            {showForm ? "⏷ hide" : "⏶ modify"} demographics
        </button>
    </div>
</div>
<div></div>

<style>
    div#demographics-wrapper {
        margin: 0 10px;
        border-radius: 10px;
        border: 1px solid var(--border-subtle);
        transition: border-color 0.15s ease;
    }
    div#demographics-wrapper:hover {
        border-color: var(--border-color);
    }

    button#toggle {
        background-color: transparent;
        border: none;
        cursor: pointer;
        font: inherit;
        color: var(--secondary-fg);
        width: 100%;
        padding: 6px 0;
        margin: 0;
        font-size: 0.72em;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: color 0.15s ease;
    }
    button#toggle:hover {
        color: var(--foreground);
    }

    div#demographics {
        display: grid;
        font-size: 0.85em;
        grid-template-columns: max-content 1fr;
        gap: 8px 12px;
        padding: 12px;
        align-items: center;
        color: var(--secondary-fg);
    }
    div#demographics input,
    div#demographics select {
        font: inherit;
        font-size: 1em;
        padding: 4px 8px;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background-color: var(--secondary-bg);
        color: var(--foreground);
        transition:
            border-color 0.15s ease,
            box-shadow 0.15s ease;
    }
    div#demographics input:focus,
    div#demographics select:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--focus-ring);
    }
</style>
