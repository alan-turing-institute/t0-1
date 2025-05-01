<script lang="ts">
    interface Props {
        darkMode: boolean;
        toggleTheme: () => void;
    }

    let { darkMode, toggleTheme }: Props = $props();
</script>

<div class="header">
    <h1>t0 online (but really gpt-4o)</h1>
    <button onclick={(_e) => toggleTheme()}>switch to {darkMode ? "light" : "dark"} mode</button>
</div>

<style>
    div.header {
        display: flex;
        gap: 20px;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: auto;
    }

    h1 {
        margin: 0;
        padding-left: 10px;
    }

    button {
        height: min-content;
        background-color: transparent;
        border: none;
        font: 0.8em;
        text-decoration: underline;
        color: var(--foreground);
    }
</style>
