<script lang="ts">
    interface Props {
        show: boolean;
    }

    let { show }: Props = $props();
</script>

<div id="loading" class={show ? "" : "hide"}>
    <span class="dot"></span>
    Thinking
</div>

<style>
    div#loading {
        width: 100%;
        text-align: left;
        margin-right: auto;
        color: var(--secondary-fg);
        font-size: 0.9em;
        font-weight: 500;
        padding: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    div#loading.hide {
        visibility: hidden;
    }

    span.dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--accent);
        animation: pulse 1.2s ease-in-out infinite;
    }

    div#loading::after {
        content: "";
        display: inline-block;
        animation: dots 1s steps(4, start) infinite;
        white-space: pre;
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 0.3;
            transform: scale(0.85);
        }
        50% {
            opacity: 1;
            transform: scale(1);
        }
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
