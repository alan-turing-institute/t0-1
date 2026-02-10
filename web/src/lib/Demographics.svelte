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
    <button class="toggle-btn" {onclick}>
        <i class="fa-solid fa-user-gear"></i>
        {showForm ? "Hide" : "Edit"} demographics
        <i class="fa-solid {showForm ? 'fa-chevron-down' : 'fa-chevron-right'} chevron"></i>
    </button>
    {#if showForm}
        <div class="demographics-card" transition:slide>
            <label>
                <span>Age</span>
                <input
                    type="number"
                    bind:value={demographics.age}
                    oninput={() => changeDemographics(demographics)}
                    {onkeydown}
                    placeholder="e.g. 30"
                />
            </label>
            <label>
                <span>Sex</span>
                <select
                    bind:value={demographics.sex}
                    onchange={() => changeDemographics(demographics)}
                    {onkeydown}
                >
                    <option value="unspecified">(select)</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                </select>
            </label>
            <label>
                <span>Occupation</span>
                <input
                    type="text"
                    bind:value={demographics.occupation}
                    oninput={() => changeDemographics(demographics)}
                    {onkeydown}
                    placeholder="e.g. Teacher"
                />
            </label>
            <label>
                <span>Support system</span>
                <input
                    type="text"
                    bind:value={demographics.supportSystem}
                    oninput={() => changeDemographics(demographics)}
                    {onkeydown}
                    placeholder="e.g. Family, friends"
                />
            </label>
            <label>
                <span>Medical history</span>
                <input
                    type="text"
                    bind:value={demographics.medicalHistory}
                    oninput={() => changeDemographics(demographics)}
                    {onkeydown}
                    placeholder="e.g. Asthma"
                />
            </label>
        </div>
    {/if}
</div>

<style>
    div#demographics-wrapper {
        display: flex;
        flex-direction: column;
    }

    .toggle-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        background: none;
        border: none;
        cursor: pointer;
        font: inherit;
        color: var(--secondary-fg);
        padding: 4px 8px;
        font-size: 0.8em;
        border-radius: 8px;
        width: max-content;
        transition: color 0.15s;
    }
    .toggle-btn:hover {
        color: var(--foreground);
    }
    .chevron {
        font-size: 0.7em;
    }

    .demographics-card {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        padding: 12px 14px;
        margin-top: 4px;
        background-color: var(--input-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        box-shadow: var(--shadow-sm);
    }

    .demographics-card label {
        display: flex;
        flex-direction: column;
        gap: 3px;
        font-size: 0.8em;
        color: var(--secondary-fg);
    }

    .demographics-card label:last-child {
        grid-column: 1 / -1;
    }

    .demographics-card input,
    .demographics-card select {
        font: inherit;
        font-size: 1em;
        padding: 6px 10px;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background-color: var(--background);
        color: var(--foreground);
        outline: none;
        transition: border-color 0.15s;
    }
    .demographics-card input:focus,
    .demographics-card select:focus {
        border-color: var(--accent);
    }
</style>
