# Plan: Route T0 Response Through Qwen Router

## Technical Notes

### How to run the system

```bash
# Start all 3 services in tmux (RAG on :8050, T0 vLLM on :8010, Qwen vLLM on :8020)
./scripts/launch-all-in-tmux.sh
```

### Key architecture

- **RAG service** (port 8050): FastAPI app orchestrating the pipeline via LangGraph. Entry: `src/t0_1/rag/rag_endpoint.py`, core: `src/t0_1/rag/build_rag.py`
- **T0 model** (port 8010): `TomasLaz/t0-1.1-k5-32B` served via vLLM. Used as `self.llm` (openai_completion provider) with budget forcing (thinking + answer tokens)
- **Qwen router** (port 8020): `Qwen/Qwen2.5-32B-Instruct` served via vLLM. Used as `self.conversational_agent_llm` (openai provider)
- Both LLMs are accessed via OpenAI-compatible HTTP APIs through LangChain wrappers

### Budget forcing format

T0 produces output in the format: `<|im_start|>think\n[reasoning]\n<|im_start|>answer\n[answer]`. The frontend (`web/src/lib/types.ts:makeAIEntry`) splits on `<|im_start|>answer` to show reasoning in a collapsible section and the answer as main content.

### LangGraph conversation graph (current)

```
START -> query_or_respond (Qwen decides: use retriever tool or respond directly)
  |-> [No tool] -> END              (Qwen responds to user for simple messages)
  |-> [Tool]   -> tools (retriever) -> process_tool_response -> [rerank?] -> generate (T0) -> END
```

When T0 is called, its response goes directly to the user. The user currently "speaks with T0" for medical queries.

---

## Context

Currently, when T0 (the reasoning model) is invoked, its response goes directly to the user. We want to change this so that:

1. T0 does clinical reasoning and produces a structured (condition, severity) prediction
2. T0's output is passed to the Qwen router with a new prompt explaining the final task
3. The router produces the final patient-friendly response explaining the condition and next action

T0's thinking tokens should still be streamed to the user as a collapsible "Reasoning" section (matching current UI behavior), while the main visible answer comes from the router.

**Severity levels** (3-level, from evaluation pipeline): Self-care / Urgent Primary Care / A&E

## New Conversation Graph Flow

```
START -> query_or_respond (Qwen)
  |-> [No tool] -> END                          (unchanged - Qwen responds directly)
  |-> [Tool]   -> tools -> process_tool_response -> [rerank?] -> generate (T0) -> router_respond (Qwen) -> END
```

## Streaming Design

The UI parses `<|im_start|>think...<|im_start|>answer...` to split reasoning (collapsible) from answer (visible). We preserve this by:

- `generate` node: Streams T0's thinking tokens only (`<|im_start|>think\n...`), suppresses answer tokens and finish signal
- `router_respond` node: Writes `\n<|im_start|>answer\n`, then streams router's response, then writes finish signal

Result: The user sees T0's reasoning accumulate in real-time (collapsible), then the router's answer appears as the main response.

---

## Files to Modify

### 1. `src/t0_1/rag/build_rag.py` (core changes)

**A. Add state field** to `CustomMessagesState` (~line 94):

```python
# T0's full output (thinking + answer), not added to conversation messages
t0_reasoning: list[str]
```

**B. Add `stream_answer` parameter** to `_budget_forcing_invoke` (~line 407) and `_budget_forcing_ainvoke` (~line 531):

- New parameter: `stream_answer: bool = True`
- When `stream_answer=False`: stream thinking tokens as usual, but suppress the answer section writes and the finish signal
- Implementation: guard the answer-phase `writer(...)` calls with `if stream_answer:`
- The thinking-phase `writer(...)` calls remain unconditional (user sees T0 thinking)

**C. Modify `generate` / `agenerate`** (~lines 738, 834) in the **conversational** branch only:

- Call budget forcing with `stream_answer=False`
- Return `t0_reasoning` instead of `messages`:
  ```python
  return {
      "system_messages": ...,
      "t0_reasoning": state.get("t0_reasoning", []) + [response.content],
      "rag_input_messages": ...,
  }
  ```
- Non-conversational branch remains unchanged (backward compatible for evaluation)

**D. Add `router_respond` and `arouter_respond` methods** to `RAG` class:

- Read `state["t0_reasoning"][-1]` (T0's latest output)
- Build message list: `[SystemMessage(ROUTER_RESPONSE_PROMPT)] + conversation_history + [HumanMessage("Clinical analysis:\n\n" + t0_output)]`
- Write `"\n<|im_start|>answer\n"` to the stream writer (signals answer section to the UI)
- Stream `self.conversational_agent_llm.stream()`/`.astream()` token by token to the stream writer
- Write finish signal
- Return `{"messages": [AIMessage(response_content)]}` (this goes into conversation history)

**E. Modify `build_conversation_graph`** (~line 959):

- Add node: `graph_builder.add_node(self.router_respond)`
- Change edge: `generate -> router_respond` (was `generate -> END`)
- Add edge: `router_respond -> END`

**F. Modify `_query_stream`** (~line 1080):

- Change streaming filter to include `router_respond`:
  ```python
  metadata.get("langgraph_node") in ["generate", "router_respond", "query_or_respond"]
  ```

### 2. `src/t0_1/rag/utils.py` (new router prompt)

Add `ROUTER_RESPONSE_PROMPT` constant alongside existing `NHS_RETRIEVER_TOOL_PROMPT`:

```
You are a helpful clinical AI assistant deployed in the United Kingdom.

Our specialist clinical reasoning model has analysed the patient's symptoms against NHS condition information. The analysis will be provided to you.

Your task is to:
1. Interpret the clinical analysis (which includes the likely condition and severity)
2. Communicate findings to the patient clearly and empathetically
3. Recommend the next action based on the severity assessment
4. Ask relevant follow-up questions to gather more information

Guidelines:
- Do NOT reveal that a separate model performed the analysis
- Do NOT mention similarity scores or technical details
- Explain conditions in simple, accessible language
- Always refer to the user in the second person
- Reply in English only
- Conclude with a question to keep the conversation going

Severity-to-action mapping:
- "Self-care": Suggest home care / over-the-counter medication, see GP if symptoms persist
- "Urgent Primary Care": Suggest seeing a GP or urgent care centre as soon as possible
- "A&E": Suggest going to A&E or calling 999 immediately
```

### 3. `templates/rag_system_prompt_conversational.txt` (refocus T0's prompt)

Change from conversational response to structured reasoning + prediction:

```
You are a clinical reasoning model specialising in NHS conditions.

You will be given a description of the user's symptoms and retrieved context from NHS condition web pages.

Your task is to:
1. Analyse the symptoms against the retrieved context
2. Determine the most likely condition(s)
3. Assess the severity level

Use similarity scores to guide your assessment but never mention them.
Focus on the most serious conditions first.

You MUST end your response with a structured prediction in exactly this format:
(condition_name, severity_level)

Where:
- condition_name is one of the retrieved source names, or "inconclusive"
- severity_level is one of: "Self-care", "Urgent Primary Care", "A&E"

Do NOT ask follow-up questions. Do NOT write a conversational response.
Focus purely on clinical reasoning and your structured prediction.

If the retrieved context is not relevant, output: (inconclusive, Self-care)

Retrieved context:
{context}

This is a summary of their demographics:
{demographics}
```

### 4. No changes needed

- **CLI** (`cli.py`): No new flags. Router prompt hardcoded in `utils.py` (matches `NHS_RETRIEVER_TOOL_PROMPT` pattern)
- **Frontend** (`web/`): Existing `makeAIEntry` parser already handles `<|im_start|>think/answer` format
- **Evaluation pipeline** (`evaluate.py`): Uses non-conversational mode, which is unchanged
- **Endpoints** (`rag_endpoint.py`): No changes needed

---

## Unit Tests (`tests/test_rag_unit.py`)

The test file uses mocked LLMs and retrievers (no vLLM or external services needed). Helper fixtures: `_make_doc`, `_make_fake_retriever`, `_make_fake_llm`, `_make_prompt_template`, `_build_test_rag`.

### Pre-existing test classes (1–11)

These 11 classes cover the current codebase. The plan changes do NOT require modifying them — they serve as **regression guards** for the non-conversational path and shared utilities.

| #   | Class                     | What it guards                                      |
| --- | ------------------------- | --------------------------------------------------- |
| 1   | `TestGraphStructure`      | Non-conversational graph nodes/edges, rerank, reset |
| 2   | `TestStateTypes`          | Field set on `State` and `CustomMessagesState`      |
| 3   | `TestRetrieverTool`       | `create_retreiver_tool`, content+artifact return    |
| 4   | `TestContextFormatting`   | `obtain_context_and_sources` with/without rerank    |
| 5   | `TestProcessToolResponse` | Query/context extraction from ToolMessages          |
| 6   | `TestPromptTemplates`     | Template loading, placeholders, NHS prompt content  |
| 7   | `TestGenerate`            | `generate`/`agenerate` in both modes, regressions   |
| 8   | `TestMemoryManagement`    | `clear_history`, `get_thread_ids`                   |
| 9   | `TestRAGEndpoint`         | FastAPI app creation, routes, request model         |
| 10  | `TestLoadLLM`             | Rejects empty/unknown LLM providers                 |
| 11  | `TestBuildRAGValidation`  | `build_rag` rejects invalid budget_forcing config   |

### New test classes (12–18) — guard the plan changes

All use mocks; no vLLM needed. They are written to **fail until the plan is implemented**.

| #   | Class                              | Tests                                                                                                                                                                                                                                                                              | What bug it catches                                                                                                                                                                                                      |
| --- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 12  | `TestRouterGraphStructure`         | `test_conversational_graph_has_router_respond_node`, `test_generate_edges_to_router_respond_not_end`, `test_router_respond_edges_to_end`, `test_non_conversational_graph_unchanged`                                                                                                | Forgetting to add `router_respond` node; wrong edges (`generate→END` instead of `generate→router_respond→END`); accidentally affecting non-conversational graph                                                          |
| 13  | `TestStateTypesRouter`             | `test_custom_messages_state_has_t0_reasoning`                                                                                                                                                                                                                                      | Missing `t0_reasoning` field on `CustomMessagesState` → runtime KeyError                                                                                                                                                 |
| 14  | `TestGenerateRouter`               | `test_generate_conversational_returns_t0_reasoning`, `test_agenerate_conversational_returns_t0_reasoning`, `test_generate_non_conversational_still_returns_messages`                                                                                                               | Conversational generate still putting T0's raw output in `messages` (user sees clinical reasoning); non-conversational path accidentally broken                                                                          |
| 15  | `TestRouterRespond`                | `test_router_respond_returns_ai_message`, `test_router_respond_uses_t0_reasoning`, `test_router_respond_writes_answer_marker`, `test_router_respond_writes_finish_signal`, `test_arouter_respond_returns_ai_message`, `test_router_respond_does_not_leak_t0_reasoning_to_messages` | `router_respond` returning wrong type; not reading T0's reasoning; missing `<\|im_start\|>answer` marker (UI never shows answer); missing finish signal (UI stuck loading); T0's raw reasoning leaking into conversation |
| 16  | `TestRouterPrompt`                 | `test_router_response_prompt_importable`, `test_router_response_prompt_has_severity_mapping`, `test_router_response_prompt_has_uk_context`                                                                                                                                         | `ROUTER_RESPONSE_PROMPT` missing from `utils.py`; prompt missing severity-to-action mapping                                                                                                                              |
| 17  | `TestConversationalTemplateChange` | `test_conversational_system_prompt_has_structured_prediction`, `test_conversational_system_prompt_no_conversational_response`                                                                                                                                                      | Template not updated to instruct T0 to produce structured `(condition, severity)` output; T0 still writing conversational responses (router's job)                                                                       |
| 18  | `TestStreamingFilter`              | `test_query_stream_yields_from_router_respond`                                                                                                                                                                                                                                     | `_query_stream` filter missing `"router_respond"` → router tokens silently dropped, user sees blank answer                                                                                                               |

---

## Manual Verification

1. **Start services**: `./scripts/launch-all-in-tmux.sh`
2. **Test simple message**: Send "Hello" via `/query_stream` - should get direct Qwen response (no reasoning)
3. **Test symptom query**: Send a symptom description - should see:
   - T0's reasoning streaming in real-time (collapsible section in UI)
   - Router's patient-friendly response as the main answer
   - Structured prediction NOT visible to user
4. **Test multi-turn**: Ask follow-up questions - router should maintain conversational context
5. **Test history**: Call `/get_history` - should show only human messages and router responses (not T0 reasoning)
6. **Test evaluation**: Run a non-conversational evaluation script - should work unchanged
