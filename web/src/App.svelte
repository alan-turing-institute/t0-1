<script lang="ts">
    import Sidebar from "./lib/Sidebar.svelte";
    import Messages from "./lib/Messages.svelte";
    import Form from "./lib/Form.svelte";
    import Error from "./lib/Error.svelte";
    import {
        type ChatEntry,
        makeHumanEntry,
        parseChatEntries,
        type Demographics,
        emptyDemographics,
        demographicsToJson,
        generateCuteUUID,
    } from "./lib/types";
    import { onMount } from "svelte";

    // HTTPS proxy
    // const HOST = "https://atit0proxy.fly.dev";

    // Locally running
    const HOST = "http://localhost:8000";

    // UI state
    let loading: boolean = $state(false);
    let error: string | null = $state(null);

    // Chat persistence and conversation management
    const NEW_CONVERSATION_ID = "__new";
    let currentId: string = $state(NEW_CONVERSATION_ID);
    let allIds: Array<string> = $state([]);
    let messages: Array<ChatEntry> = $state([]);

    function changeId(id: string) {
        console.log("changing id to", id);
        currentId = id;
        if (id !== NEW_CONVERSATION_ID) {
            loadMessages(id);
        }
    }
    function newConversation() {
        console.log("creating new conversation");
        currentId = NEW_CONVERSATION_ID;
        messages = [];
    }
    function deleteConversation(id: string) {
        fetch(`${HOST}/clear_history`, {
            method: "POST",
            body: JSON.stringify({ thread_id: id }),
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    handleError(
                        `HTTP ${response.status} error: ${response.statusText}`,
                    );
                }
                allIds = allIds.filter((thread_id) => thread_id !== id);
                if (allIds.length > 0) {
                    changeId(allIds[0]);
                } else {
                    newConversation();
                }
            })
            .catch((error) => {
                handleError(error.message);
            });
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

    // Handle demographics
    let demographics: Demographics = $state(emptyDemographics);
    function changeDemographics(newDemographics: Demographics) {
        demographics = newDemographics;
        console.log(
            "updating demographics to ",
            demographicsToJson(demographics),
        );
    }

    function handleError(err: string) {
        console.error("Error:", err);
        error = err;
        loading = false;
        // TODO: There should be a bounded queue for errors instead of just one
        setTimeout(() => {
            error = null;
        }, 10000);
    }

    function loadThreads(forceUpdateThreadId: boolean) {
        fetch(`${HOST}/get_thread_ids`, {
            method: "GET",
        })
            .then((response) => {
                if (!response.ok) {
                    handleError(
                        `HTTP ${response.status} error: ${response.statusText}`,
                    );
                }
                response.json().then((data) => {
                    allIds = data.thread_ids;
                    // There are a few situations where we might want to update the
                    // thread ID, i.e. set the active thread ID to the first one.
                    // 1. If the forceUpdateThreadId flag is set to true (i.e. during
                    // initial load)
                    // 2. If the currentId is not NEW_CONVERSATION_ID, i.e., the user is in
                    // an active conversation, but the thread ID is not in the list,
                    // that means that the conversation was deleted by somebody else.
                    // To keep the UI in sync, we should then reset the thread ID.
                    let updateThreadId =
                        forceUpdateThreadId ||
                        (currentId !== NEW_CONVERSATION_ID &&
                            !allIds.includes(currentId));
                    if (updateThreadId) {
                        if (allIds.length > 0) {
                            changeId(allIds[0]);
                        } else {
                            changeId(NEW_CONVERSATION_ID);
                        }
                    }
                    console.log("loaded thread ids", $state.snapshot(allIds));
                });
            })
            .catch((error) => {
                handleError(error.message);
            });
    }

    function loadMessages(thread_id: string) {
        const url = `${HOST}/get_history?thread_id=${thread_id}`;
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
                    console.log("received these messages from backend: ", data);
                    messages = parseChatEntries(data);
                    console.log(
                        "frontend messages set to: ",
                        $state.snapshot(messages),
                    );
                });
            })
            .catch((error) => {
                handleError(error.message);
            });
    }

    function queryLLM(query: string) {
        loading = true;

        if (currentId === NEW_CONVERSATION_ID) {
            // Generate new ID
            let newId = generateCuteUUID();
            while (allIds.includes(newId)) {
                newId = generateCuteUUID();
            }
            currentId = newId;
            // push to the front as it will be the most recent
            allIds.unshift(currentId);
        }
        messages.push(makeHumanEntry(query));

        const body = {
            query: query,
            thread_id: currentId,
            demographics: demographicsToJson(demographics),
        };
        const url = `${HOST}/query`;

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
                    console.log(
                        "received this data from querying backend: ",
                        data,
                    );
                    // We don't bother parsing the response manually here --
                    // instead we'll just load the entire conversation from the
                    // server. This is rather wasteful in terms of bandwidth,
                    // but it means that there's only one code path for parsing
                    // the response (i.e. we don't perform some kind of
                    // incremental parsing and
                    loadMessages(currentId);
                    loading = false;

                    // TODO: Keeping this code here just in case it's needed
                    // for when we implement streaming.
                    // Maybe we could just do e.g.
                    // parseChatMessages(data.response.mesesages)?
                    //
                    // const last_message =
                    //     data.response.messages[
                    //         data.response.messages.length - 1
                    //     ]
                    // if (last_message.type !== "ai") {
                    //     handleError(
                    //         "Last message was not AI, something went wrong",
                    //     );
                    //     return;
                    // }
                    // messages.push(makeAIEntry(last_message.content));
                });
            })
            .catch((error) => {
                handleError(error.message);
            });
    }

    let backendReady: boolean = $state(false);
    function startup() {
        // Check if backend is running
        fetch(`${HOST}`, {
            method: "GET",
        }).then((response) => {
            if (response.ok) {
                response.json().then((_) => {
                    console.log("pinged backend successfully");
                    backendReady = true;
                    loadThreads(true);
                });
            }
        });
    }

    onMount(() => {
        startup();

        setInterval(() => {
            if (backendReady) {
                loadThreads(false);
            }
        }, 5000);
    });
</script>

<div id="wrapper">
    <Sidebar
        {currentId}
        {loading}
        {allIds}
        {changeId}
        {newConversation}
        {deleteConversation}
        {darkMode}
        {toggleTheme}
    />
    {#if backendReady}
        <main>
            <Error {error} />
            <Messages history={messages} {loading} />
            <Form {loading} {queryLLM} {changeDemographics} />
        </main>
    {:else}
        <p id="no-backend">
            <span>Failed to connect to backend at <code>{HOST}</code>.</span>
            <span>Please check if the backend is running.</span>
            <span
                >If you want to change the backend URL, please edit <code
                    >web/src/App.svelte</code
                >
                and change the <code>HOST</code> constant.</span
            >
        </p>
    {/if}
</div>

<style>
    :global(*) {
        transition:
            background-color 0.5s ease-out,
            color 0.5s ease-out;
    }

    div#wrapper {
        display: flex;
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
        min-width: 300px;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: end;
    }

    p#no-backend {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: auto;
        padding: 0 30px;
        text-align: center;
        color: var(--foreground);
    }
</style>
