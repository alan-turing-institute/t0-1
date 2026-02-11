# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web frontend for **t0**, a RAG (Retrieval-Augmented Generation) chat interface for NHS health conditions. Built by the Alan Turing Institute. Users ask health questions and get AI-generated answers backed by NHS A-to-Z condition pages, with optional reasoning display and source links.

## Commands

- `pnpm dev` — Start dev server (localhost:5173)
- `pnpm build` — Production build
- `pnpm preview` — Preview production build
- `pnpm check` — Type-check (svelte-check + tsc)
- `pnpm serve-rag` — Start the local RAG backend (requires Python venv at `../.venv`)

The backend must be running for the frontend to work. Without it, the UI shows a connection error.

## Tech Stack

- **Svelte 5** with runes (`$state`, `$derived`, `$props`, `$effect`) — not legacy Svelte stores
- **TypeScript** with strict checking
- **Vite** for dev server and builds
- **pnpm** as package manager (not npm/yarn)

## Architecture

### Backend Communication

`App.svelte` owns all backend communication. The backend URL is hardcoded as `HOST` at the top of `App.svelte` (toggle between Azure proxy and localhost there). Key endpoints:

- `GET /` — health check
- `GET /get_thread_ids` — list conversations
- `GET /get_history?thread_id={id}` — load conversation messages
- `POST /query_stream` — send query, get streamed response
- `POST /clear_history` — delete a conversation
- `GET /new_thread_id` — create a new conversation thread

Responses are streamed via `ReadableStream` and decoded chunk-by-chunk in `queryLLM()`.

### Message Parsing (`src/lib/types.ts`)

The backend returns messages containing special tokens: `<|im_start|>think` and `<|im_start|>answer` to delimit reasoning from the final answer. `makeAIEntry()` parses these tokens to split reasoning/answer, then converts Markdown to sanitized HTML (showdown + sanitize-html). Tool messages extract NHS source URLs from `entry.artifact.context`.

### State Management

All app state lives in `App.svelte` using Svelte 5 `$state` runes and is passed down as props. There are no stores. Key state: `messages`, `currentId`, `allIds`, `loading`, `error`, `demographics`, `darkMode`.

### Theming

Dark/light mode uses CSS custom properties on `html[data-theme]` defined in `app.css`. Theme preference is persisted in localStorage (`t0web___darkMode`). A duplicate `getDarkModePreference()` exists in both `index.html` (to prevent flash) and `App.svelte`.

### Component Hierarchy

```
App.svelte          — orchestrator, backend calls, all state
├── Sidebar         — conversation list, new/delete chat, theme toggle
├── Error           — auto-dismissing error banner (10s timeout)
├── Messages        — chat history display, auto-scroll to latest human message
│   ├── Loading     — animated "Thinking..." indicator
│   └── Reasoning   — expandable reasoning section
└── Form            — auto-growing textarea, submit handler
    └── Demographics — collapsible form for user context (age, sex, etc.)
```
