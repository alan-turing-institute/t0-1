<script lang="ts">
    import Messages from "./lib/Messages.svelte";
    import Form from "./lib/Form.svelte";
    import Header from "./lib/Header.svelte";
    import Error from "./lib/Error.svelte";
    import { type ChatEntry, makeHumanEntry, makeAIEntry } from "./lib/types";

    let history: Array<ChatEntry> = $state([]);
    let disableForm: boolean = $state(false);
    let loading: boolean = $state(false);
    let error: string | null = $state(null);

    function getDarkModePreference(): boolean {
        const localStorageOption = localStorage.getItem("darkMode");
        if (localStorageOption === "true") {
            return true;
        } else if (localStorageOption === "false") {
            return false;
        } else {
            return window.matchMedia("(prefers-color-scheme: dark)").matches;
        }
    }
    let darkMode: boolean = $state(getDarkModePreference());
    let darkModePreference: string = $derived(darkMode ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", darkModePreference);
    function toggleTheme() {
        darkMode = !darkMode;
        document.documentElement.setAttribute("data-theme", darkModePreference);
        localStorage.setItem("darkMode", darkMode.toString());
    }

    function handleError(err: string) {
        console.error("Error:", err);
        error = err;
        loading = false;
        disableForm = false;
        setTimeout(() => {
            error = null;
        }, 10000);
    }

    function queryLLM(query: string) {
        disableForm = true;
        history.push(makeHumanEntry(query));

        const host = "http://localhost";
        const port = 8000;
        const params = new URLSearchParams([["query", query]]).toString();
        const url = `${host}:${port}/query?${params}`;

        loading = true;
        fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    // TODO Handle nicely -- 404s and stuff go here
                    handleError(
                        `HTTP ${response.status} error: ${response.statusText}`,
                    );
                }
                response.json().then((data) => {
                    // TODO convert Markdown into HTML
                    console.log(data);
                    const last_message =
                        data.response.messages[
                            data.response.messages.length - 1
                        ];
                    if (last_message.type !== "ai") {
                        handleError(
                            "Last message was not AI, something went wrong",
                        );
                        return;
                    }
                    loading = false;
                    history.push(makeAIEntry(last_message.content));
                    disableForm = false;
                });
            })
            .catch((error) => {
                handleError(error.message);
            });
    }
</script>

<div id="wrapper">
    <Error {error} />
    <main>
        <Header {darkMode} {toggleTheme}></Header>
        <Messages {history} {loading} />
        <Form {disableForm} {queryLLM} />
    </main>
</div>

<style>
    :global(html) {
        --background: #f8f8f8;
        --foreground: #151515;
        --user-message-bg: #e2e2e2;
        --secondary-fg: #646464;
        --secondary-bg: #ffffff;
        --highlight: #007acc;
        --error: #ff0000;
    }
    :global(html[data-theme="dark"]) {
        --background: #1e1e1e;
        --foreground: #d8d8d8;
        --user-message-bg: #484848;
        --secondary-fg: #939393;
        --secondary-bg: #000000;
        --highlight: #007acc;
        --error: #ff0000;
    }
    :global(*) {
        transition:
            background-color 0.5s ease-out,
            color 0.5s ease-out;
    }

    div#wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100vw;
        height: 100vh;
        background-color: var(--background);
        color: var(--foreground);
    }

    main {
        min-width: 300px;
        width: 700px;
        max-width: calc(100% - 80px);
        height: calc(100% - 80px);
        margin: 40px 0;
        display: flex;
        flex-direction: column;
        align-items: left;
        justify-content: end;
        gap: 20px;
    }
</style>
