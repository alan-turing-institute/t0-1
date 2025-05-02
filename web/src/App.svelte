<script lang="ts">
    import Messages from "./lib/Messages.svelte";
    import Form from "./lib/Form.svelte";
    import Header from "./lib/Header.svelte";
    import Error from "./lib/Error.svelte";
    import {
        type ChatEntry,
        makeHumanEntry,
        makeAIEntry,
        parseChatEntries,
    } from "./lib/types";
    import { onMount } from "svelte";

    // UI state
    let disableForm: boolean = $state(false);
    let loading: boolean = $state(false);
    let error: string | null = $state(null);

    // Chat persistence and conversation management
    let currentId: string = $state(
        localStorage.getItem("t0web___currentId") ?? "",
    );
    let allIds: Array<string> = $state([]);
    let messages: Array<ChatEntry> = $state([]);
    const LS_ALLIDS_KEY = "t0web___allIds";
    const LS_CURRENTID_KEY = "t0web___currentId";

    onMount(() => {
        const localStorageIds = localStorage.getItem(LS_ALLIDS_KEY);
        if (localStorageIds) {
            allIds = JSON.parse(localStorageIds);
        }
        if (allIds.length === 0) {
            newConversation();
        }
    });
    function changeId(id: string) {
        currentId = id;
        loadMessages(id);
    }
    function newConversation() {
        currentId = crypto.randomUUID();
        allIds.push(currentId);
        messages = [];
    }
    function deleteCurrentConversation() {
        const idx = allIds.indexOf(currentId);
        allIds = allIds.filter((id) => id !== currentId);
        if (allIds.length === 0) {
            newConversation();
        } else {
            currentId = allIds[idx === 0 ? 0 : idx - 1];
        }
    }
    $effect(() => {
        localStorage.setItem(LS_CURRENTID_KEY, currentId);
        loadMessages(currentId);
    });
    $effect(() => {
        localStorage.setItem(LS_ALLIDS_KEY, JSON.stringify(allIds));
    });

    // Dark mode management
    const LS_DARKMODE_KEY = "t0web___darkMode";
    function getDarkModePreference(): boolean {
        const localStorageOption = localStorage.getItem(LS_DARKMODE_KEY);
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
    function toggleTheme() {
        darkMode = !darkMode;
        document.documentElement.setAttribute("data-theme", darkModePreference);
        localStorage.setItem(LS_DARKMODE_KEY, darkMode.toString());
    }

    // API queries
    const HOST = "http://localhost";
    const PORT = 8000;

    function handleError(err: string) {
        console.error("Error:", err);
        error = err;
        loading = false;
        disableForm = false;
        setTimeout(() => {
            error = null;
        }, 10000);
    }

    function loadMessages(thread_id: string) {
        const url = `${HOST}:${PORT}/get_history?thread_id=${thread_id}`;
        fetch(url, {
            method: "GET",
        })
            .then((response) => {
                if (!response.ok) {
                    // If 404, no thread found
                    if (response.status === 404) {
                        messages = [];
                        console.log(
                            "No thread found, messages set to empty array",
                        );
                        return;
                    } else {
                        handleError(
                            `HTTP ${response.status} error: ${response.statusText}`,
                        );
                    }
                }
                response.json().then((data) => {
                    messages = parseChatEntries(data);
                    console.log("loaded messages", $state.snapshot(messages));
                });
            })
            .catch((error) => {
                handleError(error.message);
            });
    }

    function queryLLM(query: string) {
        disableForm = true;
        messages.push(makeHumanEntry(query));

        const body = {
            query: query,
            thread_id: currentId,
        };
        const url = `${HOST}:${PORT}/query`;

        loading = true;
        fetch(url, {
            method: "POST",
            body: JSON.stringify(body),
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
                    messages.push(makeAIEntry(last_message.content));
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
        <Header
            {allIds}
            {currentId}
            {changeId}
            {newConversation}
            {deleteCurrentConversation}
            {darkMode}
            {toggleTheme}
        ></Header>
        <Messages history={messages} {loading} />
        <Form {disableForm} {queryLLM} />
    </main>
</div>

<style>
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
