<script lang="ts">
  import { slide } from "svelte/transition";

  interface Props {
    currentId: string;
    loading: boolean;
    allIds: Array<string>;
    changeId: (id: string) => void;
    newConversation: () => void;
    deleteConversation: (id: string) => void;
    darkMode: boolean;
    toggleTheme: () => void;
  }

  let {
    currentId,
    loading,
    allIds,
    changeId,
    newConversation,
    deleteConversation,
    darkMode,
    toggleTheme,
  }: Props = $props();
</script>

<div class="sidebar">
  <div class="sidebar-tophalf">
    <h1>t0.1 online</h1>
    <p class="subheading">
      Private knowledge retrieval and reasoning on local systems
    </p>
    <div class="sidebar-buttons">
      <span><i>Select conversation:</i></span>
      <div class="conversations">
        {#each allIds as id}
          <div class="conversation-manager" transition:slide>
            <input
              {id}
              type="radio"
              value={id}
              name="conversation"
              onchange={() => changeId(id)}
              bind:group={currentId}
              disabled={loading}
              hidden
            />
            <label for={id}>{id}</label>
            <button
              class="delete-conversation"
              onclick={() => deleteConversation(id)}
              disabled={loading}
              aria-label="Delete conversation"
            >
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        {/each}
      </div>
    </div>
  </div>
  <div id="button-wrapper">
    <a
      href="https://www.turing.ac.uk/research/research-projects/project-t0"
      target="_blank"
      rel="noopener noreferrer"
      class="qr-link"
    >
      <img
        src="qr-project-t0.svg"
        alt="QR code for Project t0"
        class="qr-code"
      />
    </a>
    <button
      class="sidebar-bottom {currentId === '__new' ? 'bold' : ''}"
      id="newconv"
      onclick={(_e) => newConversation()}>new conversation</button
    >
    <button class="sidebar-bottom" id="darkmode" onclick={(_e) => toggleTheme()}
      >switch to {darkMode ? "light" : "dark"} mode</button
    >
  </div>
</div>

<style>
  div.sidebar {
    height: 100%;
    width: 260px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 32px 16px;
    align-items: stretch;
    justify-content: space-between;
    flex: 0 0 auto;
    background-color: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    transition:
      background-color 0.3s ease,
      border-color 0.3s ease;
  }

  div.sidebar-tophalf {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
  }

  h1 {
    margin: 0 0 4px 8px;
    font-size: 1.2em;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--accent);
  }

  p.subheading {
    margin: 0 0 24px 8px;
    font-size: 0.85em;
    font-weight: 400;
    color: var(--secondary-fg);
    line-height: 1.3;
  }

  div.sidebar-buttons {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-height: 100px;
    max-height: calc(100vh - 270px);
    align-items: stretch;
  }

  div.sidebar-buttons > span {
    font-size: 0.75em;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--secondary-fg);
    padding-left: 8px;
  }

  div.conversations {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 2px;
    align-items: stretch;
    padding-right: 4px;
    overflow-y: auto;
  }

  div.conversation-manager {
    width: 100%;
    display: flex;
    gap: 4px;
    align-items: center;
    justify-content: space-between;
    padding: 6px 8px;
    border-radius: 6px;
    transition: background-color 0.15s ease;

    &:hover {
      background-color: var(--sidebar-hover);
    }

    label {
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      font-size: 0.85em;
      margin: 0;
      padding: 0;
      cursor: pointer;
      color: var(--foreground);
    }
    input:disabled + label {
      cursor: default;
      opacity: 0.6;
    }

    input:checked + label {
      font-weight: 600;
      color: var(--accent);
    }

    button.delete-conversation {
      flex: 0 0 auto;
      background-color: transparent;
      color: var(--secondary-fg);
      text-decoration: none;
      border: none;
      padding: 2px 4px;
      border-radius: 4px;
      font-size: 0.8em;
      opacity: 0;
      transition:
        opacity 0.15s ease,
        color 0.15s ease;
    }
    &:hover button.delete-conversation {
      opacity: 1;
    }
    button.delete-conversation:hover {
      color: var(--error);
      cursor: pointer;
    }
  }

  /* Active conversation background */
  div.conversation-manager:has(input:checked) {
    background-color: var(--sidebar-active);
  }

  a.qr-link {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
  }

  img.qr-code {
    width: 120px;
    height: 120px;
    border-radius: 8px;
    background-color: white;
    padding: 0.1px;
  }

  div#button-wrapper {
    flex: 0 0 auto;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 0 4px;

    button.sidebar-bottom {
      font: inherit;
      font-size: 0.85em;
      height: min-content;
      background-color: transparent;
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      color: var(--foreground);
      cursor: pointer;
      padding: 8px 12px;
      text-align: left;
      transition:
        background-color 0.15s ease,
        border-color 0.15s ease;
    }

    button.sidebar-bottom:hover {
      background-color: var(--sidebar-hover);
      border-color: var(--border-color);
    }

    button.sidebar-bottom.bold {
      font-weight: 600;
      color: var(--accent);
      border-color: var(--accent);
    }
  }
</style>
