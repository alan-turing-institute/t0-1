<div id="loading">Thinking</div>

<style>
    div#loading {
        width: 100%;
        text-align: left;
        margin-right: auto;
        color: var(--secondary-fg);
        font-size: 0.9em;
        padding: 10px;
    }

    div#loading::after {
        content: "";
        display: inline-block;
        animation: dots 1s steps(4, start) infinite;
        white-space: pre;
    }

    @keyframes dots {
        0% {
            content: "";
        }
        20% {
            content: ".";
        }
        40% {
            content: "..";
        }
        60% {
            content: "...";
        }
        100% {
            content: "...";
        }
    }
</style>
