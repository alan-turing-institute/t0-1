<script lang="ts">
    type ChatEntry = {
        role: "user" | "response";
        content: string;
    };
    function makeUserEntry(message: string): ChatEntry {
        return { role: "user", content: message };
    }
    function makeResponseEntry(message: string): ChatEntry {
        return { role: "response", content: message };
    }

    let message: string = "";
    let chatlog: Array<ChatEntry> = [];
    let disableForm: boolean = false;
    let chatLogDiv: HTMLDivElement | null = null;

    function queryLLM(query: string) {
        const host = "http://0.0.0.0";
        const port = 8000;
        const params = new URLSearchParams([["query", query]]).toString();
        const url = `${host}:${port}/query?${params}`;

        fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }).then((response) => {
            if (!response.ok) {
                // TODO Handle nicely
                throw new Error(`HTTP error, status: ${response.status}`);
            }
            response.json().then((data) => {
                // TODO convert Markdown into HTML
                console.log(data);
                chatlog = [...chatlog, makeResponseEntry(data.response.answer.content) ];
                scrollToBottom();
                disableForm = false;
            });
        });
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSubmit(event);
        }
    }

    function handleSubmit(event: Event) {
        event.preventDefault();
        if (message.trim() === "" || disableForm) {
            return;
        }
        chatlog = [...chatlog, makeUserEntry(message)];
        scrollToBottom();
        disableForm = true;
        queryLLM(message);
        message = "";
    }

    function scrollToBottom() {
        if (chatLogDiv) {
            setTimeout(() => {
                chatLogDiv.scrollTop = chatLogDiv.scrollHeight;
            }, 100);
        }
    }
</script>

<main>
    <div class="chatlog" bind:this={chatLogDiv}>
        {#each chatlog as entry}
            <div class={entry.role}>
                {entry.content}
            </div>
        {/each}
    </div>

    <form id="chat" on:submit|preventDefault={handleSubmit}>
        <textarea
            bind:value={message}
            placeholder="Your message here..."
            on:keydown={handleKeyDown}
        ></textarea>
        <button type="submit" disabled={disableForm}>Send</button>
    </form>
</main>

<style>
main {
    min-width: 300px;
    width: calc(100% - 40px);
    max-width: 800px;
    height: calc(100vh - 80px);
    margin: 40px auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    border: 1px solid black;
}

div.chatlog {
    width: 100%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding-bottom: 20px;
    scroll-behavior: smooth;
}

div.user, div.response {
    width: max-content;
    max-width: 60%;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid black;
}

div.user {
    text-align: right;
    margin-left: auto;
}

div.response {
    text-align: left;
    margin-right: auto;
}


form {
    border: 1px solid blue;
    width: 100%;
    display: flex;
    gap: 10px;
}

textarea, button {
    font-size: inherit;
}

textarea {
    width: 100%;
    font-family: "Fira Mono", monospace;
}

button {
    font-family: inherit;
}
</style>
