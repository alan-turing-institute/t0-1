<script lang="ts">
    import Messages from "./lib/Messages.svelte";
    import Form from "./lib/Form.svelte";
    import Header from "./lib/Header.svelte";
    import Error from "./lib/Error.svelte";
    import { type ChatEntry, makeHumanEntry, makeAIEntry } from "./lib/types";
    import { onMount } from "svelte";
    // NOTE about SvelteMap:
    // 1. It doesn't need to be wrapped in $state. Odd.
    // 2. It is not deeply reactive, in that if m.get("a") is an array and you
    //    push to that array, it won't trigger a reactivity update. You need to
    //    use the Map methods, i.e. set, to trigger reactivity.
    // 3. Another way of triggering reactivity is to use the $state function --
    //    but not on the top-level map -- rather on the values themselves.
    //    We don't do this here, but it is an option.
    // See:
    // https://svelte.dev/docs/svelte/svelte-reactivity#SvelteMap
    // https://github.com/sveltejs/svelte/issues/14386
    import { SvelteMap } from "svelte/reactivity";

    let currentId: string = $state("");
    let history: SvelteMap<string, Array<ChatEntry>> = new SvelteMap();
    let allIds: Array<string> = $derived([...history.keys()]);
    function changeId(id: string) {
        currentId = id;
    }
    let disableForm: boolean = $state(false);
    let loading: boolean = $state(false);
    let error: string | null = $state(null);
    function newConversation() {
        currentId = crypto.randomUUID();
        history.set(currentId, []);
    }
    onMount(newConversation);
    function addMessage(entry: ChatEntry) {
        // This method used to reactivity on the map. See comments above the
        // SvelteMap import.
        const messages = history.get(currentId);
        history.set(currentId, [...messages, entry]);
    }

    const darkModeKey = "t0web___darkMode";
    function getDarkModePreference(): boolean {
        const localStorageOption = localStorage.getItem(darkModeKey);
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
        localStorage.setItem(darkModeKey, darkMode.toString());
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
        addMessage(makeHumanEntry(query));

        const host = "http://localhost";
        const port = 8000;
        const body = {
            query: query,
            thread_id: currentId,
        };
        const url = `${host}:${port}/query`;

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
                    addMessage(makeAIEntry(last_message.content));
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
        <Header {allIds} {currentId} {changeId} {newConversation} {darkMode} {toggleTheme}></Header>
        <Messages history={history.get(currentId)} {loading} />
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
