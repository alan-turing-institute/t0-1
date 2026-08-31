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
    } from "./lib/types";
    import { onMount } from "svelte";

    // HTTPS proxy
    const HOST = "https://t0-reverse-proxy.azurewebsites.net";
    // Or run locally:
    // const HOST = "http://localhost:8000";

    // UI state
    let loading: boolean = $state(false);
    let error: string | null = $state(null);
    let sidebarOpen: boolean = $state(false);

    function toggleSidebar() {
        sidebarOpen = !sidebarOpen;
    }
    function closeSidebar() {
        sidebarOpen = false;
    }

    // Chat persistence and conversation management
    const NEW_CONVERSATION_ID = "__new";
    let currentId: string = $state(NEW_CONVERSATION_ID);
    let allIds: Array<string> = $state([]);
    let messages: Array<ChatEntry> = $state([]);

    async function changeId(id: string) {
        console.log("changing id to", id);
        currentId = id;
        if (id !== NEW_CONVERSATION_ID) {
            messages = await loadMessages(id);
        }
    }
    function newConversation() {
        console.log("creating new conversation");
        currentId = NEW_CONVERSATION_ID;
        messages = [];
    }
    async function deleteConversation(id: string) {
        const resp = await fetch(`${HOST}/clear_history`, {
            method: "POST",
            body: JSON.stringify({ thread_id: id }),
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (!resp.ok) {
            handleError(`HTTP ${resp.status} error: ${resp.statusText}`);
            return;
        }

        allIds = allIds.filter((thread_id) => thread_id !== id);
        if (allIds.length > 0) {
            changeId(allIds[0]);
        } else {
            newConversation();
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

    async function loadThreads(forceUpdateThreadId: boolean) {
        const resp = await fetch(`${HOST}/get_thread_ids`, {
            method: "GET",
        });
        if (!resp.ok) {
            handleError(`HTTP ${resp.status} error: ${resp.statusText}`);
            return;
        }

        const data = await resp.json();
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
            (currentId !== NEW_CONVERSATION_ID && !allIds.includes(currentId));
        if (updateThreadId) {
            if (allIds.length > 0) {
                changeId(allIds[0]);
            } else {
                changeId(NEW_CONVERSATION_ID);
            }
        }
        console.log("loaded thread ids", $state.snapshot(allIds));
    }

    async function loadMessages(thread_id: string) {
        const url = `${HOST}/get_history?thread_id=${thread_id}`;
        const resp = await fetch(url, {
            method: "GET",
        });

        if (!resp.ok) {
            // If 404, no thread found
            if (resp.status === 404) {
                messages = [];
                console.log("No thread found, messages set to empty array");
                return;
            } else {
                handleError(`HTTP ${resp.status} error: ${resp.statusText}`);
            }
        } else {
            const data = await resp.json();
            console.log("received these messages from backend: ", data);
            console.log(
                "parsed as: ",
                $state.snapshot(messages),
            );
            return parseChatEntries(data);
        }
    }

    async function getNewThreadId() {
        const url = `${HOST}/new_thread_id`;
        const resp = await fetch(url, { method: "GET" });
        if (!resp.ok) {
            handleError(`HTTP ${resp.status} error: ${resp.statusText}`);
        } else {
            const data = await resp.json();
            console.log("received new thread id from backend: ", data);
            return data.thread_id;
        }
    }

    let nextMessage: string = $state("");
    async function queryLLM(query: string) {
        loading = true;

        if (currentId === NEW_CONVERSATION_ID) {
            let newId = await getNewThreadId();
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
        const url = `${HOST}/query_stream`;

        const resp = await fetch(url, {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "Content-Type": "application/json",
            },
        });
        if (!resp.ok) {
            // TODO Handle nicely -- 404s and stuff go here
            handleError(`HTTP ${resp.status} error: ${resp.statusText}`);
        } else {
            console.log(resp);

            const dc = new TextDecoder();

            for await (const chunk of resp.body) {
                nextMessage += dc.decode(chunk);
            }

            messages = await loadMessages(currentId);
            nextMessage = "";
            loading = false;
        }
    }

    let backendReady: boolean = $state(false);

    // --- DEV MOCK: remove this block after testing mobile layout ---
    const USE_MOCK = false;
    function loadMockData() {
        backendReady = true;
        allIds = ["thread-abc-123", "thread-def-456", "thread-ghi-789"];
        currentId = "thread-abc-123";
        messages = [
            {
                role: "human",
                content: "<p>What are the common symptoms of a cold versus the flu?</p>",
            },
            {
                role: "ai",
                content:
                    "<p>Both colds and the flu share some symptoms, but there are key differences:</p>" +
                    "<ul><li><strong>Common cold:</strong> runny or stuffy nose, sore throat, sneezing, mild cough, low-grade fever</li>" +
                    "<li><strong>Flu:</strong> sudden onset of high fever, body aches, chills, fatigue, headache, dry cough</li></ul>" +
                    "<p>The flu tends to come on quickly and feels more severe, while a cold develops gradually. If you're unsure, a GP can help determine which one you have.</p>",
                reasoning:
                    "<p>The user is asking about symptom differences between cold and flu. I should provide a clear comparison without making a diagnosis.</p>",
            },
            {
                role: "human",
                content: "<p>I've had a headache for 3 days and paracetamol isn't helping. Should I be worried?</p>",
            },
            {
                role: "ai",
                content:
                    "<p>A persistent headache lasting several days that doesn't respond to over-the-counter painkillers is worth getting checked out. You should see your GP, especially if you also experience:</p>" +
                    "<ul><li>Vision changes</li><li>Nausea or vomiting</li><li>Stiff neck</li><li>Fever</li><li>Confusion</li></ul>" +
                    "<p>It's likely nothing serious, but a healthcare professional can properly assess your symptoms and rule out anything that needs further investigation.</p>",
                reasoning: null,
            },
        ];
    }
    // --- END DEV MOCK ---

    function startup() {
        // Check if backend is running
        if (USE_MOCK) {
            loadMockData();
            return;
        }
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

        // setInterval(() => {
        //     if (backendReady) {
        //         loadThreads(false);
        //     }
        // }, 5000);
    });
</script>

<div id="wrapper">
    <button class="hamburger" onclick={toggleSidebar} aria-label="Toggle sidebar">
        <i class="fa-solid {sidebarOpen ? 'fa-xmark' : 'fa-bars'}"></i>
    </button>

    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    {#if sidebarOpen}
        <div class="sidebar-overlay" onclick={closeSidebar}></div>
    {/if}

    <div class="sidebar-container" class:open={sidebarOpen}>
        <Sidebar
            {currentId}
            {loading}
            {allIds}
            changeId={(id) => { changeId(id); closeSidebar(); }}
            newConversation={() => { newConversation(); closeSidebar(); }}
            {deleteConversation}
            {darkMode}
            {toggleTheme}
        />
    </div>

    {#if backendReady}
        <main>
            <Error {error} />
            <Messages history={messages} {loading} {nextMessage} />
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
    div#wrapper {
        display: flex;
        align-items: stretch;
        height: 100vh;
        width: 100vw;
        background-color: var(--background);
        color: var(--foreground);
        transition:
            background-color 0.3s ease,
            color 0.3s ease;
    }

    .hamburger {
        display: none;
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 30;
        background-color: var(--sidebar-bg);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        color: var(--foreground);
        width: 44px;
        height: 44px;
        font-size: 1.2em;
        cursor: pointer;
        align-items: center;
        justify-content: center;
        transition:
            background-color 0.15s ease,
            border-color 0.15s ease;
    }
    .hamburger:hover {
        background-color: var(--sidebar-hover);
        border-color: var(--border-color);
    }

    .sidebar-overlay {
        display: none;
    }

    .sidebar-container {
        flex: 0 0 auto;
    }

    main {
        height: calc(100vh - 60px);
        margin: 30px auto;
        padding: 0 24px;
        width: 100%;
        max-width: 860px;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: end;
    }

    p#no-backend {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin: auto;
        padding: 0 30px;
        text-align: center;
        color: var(--secondary-fg);
        line-height: 1.6;
    }
    p#no-backend code {
        background-color: var(--accent-subtle);
        color: var(--accent);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85em;
    }

    @media (max-width: 768px) {
        .hamburger {
            display: flex;
        }

        .sidebar-overlay {
            display: block;
            position: fixed;
            inset: 0;
            z-index: 15;
            background-color: rgba(0, 0, 0, 0.4);
        }

        .sidebar-container {
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            z-index: 20;
            transform: translateX(-100%);
            transition: transform 0.25s ease;
        }
        .sidebar-container.open {
            transform: translateX(0);
        }

        main {
            margin: 30px auto 20px;
            padding: 0 12px;
            padding-top: 36px;
        }

        p#no-backend {
            padding: 60px 16px 0;
        }
    }
</style>
