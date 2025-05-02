<script lang="ts">
    import Sidebar from "./lib/Sidebar.svelte";
    import Messages from "./lib/Messages.svelte";
    import Form from "./lib/Form.svelte";
    import Error from "./lib/Error.svelte";
    import {
        type ChatEntry,
        makeHumanEntry,
        makeAIEntry,
        parseChatEntries,
    } from "./lib/types";
    import { onMount } from "svelte";

    const HOST = "http://localhost";
    const PORT = 8000;

    // UI state
    let disableForm: boolean = $state(false);
    let loading: boolean = $state(false);
    let error: string | null = $state(null);

    // Chat persistence and conversation management
    let currentId: string = $state("new");
    let allIds: Array<string> = $state([]);
    let messages: Array<ChatEntry> = $state([]);

    fetch(`${HOST}:${PORT}/get_thread_ids`, {
        method: "GET",
    })
        .then((response) => {
            if (!response.ok) {
                // TODO: This probably means the backend isn't running. We
                // should have a more in-your-face-error.
                handleError(
                    `HTTP ${response.status} error: ${response.statusText}`,
                );
            }
            response.json().then((data) => {
                allIds = data.thread_ids;
                if (allIds.length > 0) {
                    changeId(allIds[0]);
                }
                console.log("loaded thread ids", $state.snapshot(allIds));
            });
        })
        .catch((error) => {
            // TODO: This probably means the backend isn't running. We
            // should have a more in-your-face-error.
            handleError(error.message);
        });

    function changeId(id: string) {
        currentId = id;
        loadMessages(id);
    }
    function newConversation() {
        currentId = "new";
        messages = [];
    }
    function deleteConversation(id: string) {
        const idx = allIds.indexOf(id);
        allIds = allIds.filter((x) => x !== id);
        if (allIds.length === 0) {
            newConversation();
        }
        if (id == currentId) {
            currentId = allIds[idx === 0 ? 0 : idx - 1];
        }
    }

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

        if (currentId === "new") {
            currentId = crypto.randomUUID();
            // push to the front as it will be the most recent
            allIds.unshift(currentId);
        }
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
    <Sidebar
        {allIds}
        {changeId}
        {newConversation}
        {deleteConversation}
        {darkMode}
        {toggleTheme}
    />
    <main>
        <Error {error} />
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
        align-items: stretch;
        height: 100vh;
        min-width: 300px;
        width: 100vw;
        background-color: var(--background);
        color: var(--foreground);
    }

    main {
        height: calc(100vh - 60px);
        margin: 30px;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: left;
        justify-content: end;
        gap: 20px;
    }
</style>
