<script lang="ts">
    interface Props {
        show: boolean;
    }

    let { show }: Props = $props();
</script>

<div id="loading" class={show ? "" : "hide"}>
    <div class="dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
    </div>
</div>

<style>
    div#loading {
        width: 100%;
        text-align: left;
        padding: 8px 4px 8px 44px;
    }

    div#loading.hide {
        visibility: hidden;
    }

    .dots {
        display: inline-flex;
        gap: 4px;
        align-items: center;
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--secondary-fg);
        animation: bounce 1.4s ease-in-out infinite;
    }

    .dot:nth-child(1) {
        animation-delay: 0s;
    }
    .dot:nth-child(2) {
        animation-delay: 0.16s;
    }
    .dot:nth-child(3) {
        animation-delay: 0.32s;
    }

    @keyframes bounce {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
        }
        30% {
            transform: translateY(-6px);
            opacity: 1;
        }
    }
</style>
