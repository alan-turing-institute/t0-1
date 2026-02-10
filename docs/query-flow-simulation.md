# Query Flow Simulation

**Query:** `"I have fever and a cough since last week"`  
**Mode:** Conversational (with budget forcing enabled)  
**Thread:** `sunny-otter-42` (new session, no prior messages)  
**Demographics:** `None` (not provided)

---

## Architecture Recap

```
POST /query_stream  ──►  _query_stream()  ──►  LangGraph conversation graph

  START
    │
    ▼
  query_or_respond  (Qwen  – port 8020)
    │
    ├── [No tool call] ──► END   (simple greetings etc.)
    │
    └── [Tool call] ──► tools (retriever)
                            │
                            ▼
                       process_tool_response
                            │
                            ▼
                        generate  (T0  – port 8010, budget forcing)
                            │
                            ▼
                      router_respond  (Qwen  – port 8020)
                            │
                            ▼
                           END
```

---

## Step 0 — HTTP Entry Point

**Component:** `rag_endpoint.py → POST /query_stream`

The user's frontend sends:

```json
{
  "query": "I have fever and a cough since last week",
  "thread_id": "sunny-otter-42",
  "demographics": null
}
```

This is parsed into a `QueryRequest` Pydantic model, then calls:

```python
rag._query_stream(
    question="I have fever and a cough since last week",
    thread_id="sunny-otter-42",
    demographics=None,
)
```

**Returns:** a `StreamingResponse` wrapping the generator from `_query_stream`.

### Initial graph input

`_query_stream` builds the input dict for the conversational graph:

```python
input = {
    "messages": {"role": "user", "content": "I have fever and a cough since last week"},
    "demographics": None,
}
```

LangGraph automatically converts this into the `CustomMessagesState` with:

```python
{
    "messages": [HumanMessage(content="I have fever and a cough since last week")],
    "demographics": None,
    # all other fields initialised to defaults/empty
}
```

---

## Step 1 — `query_or_respond` (Qwen Router decides: tool or reply?)

**Component:** `build_rag.py → RAG.query_or_respond()`  
**LLM:** Qwen 2.5-32B-Instruct (port 8020) — `self.conversational_agent_llm`

### What happens

1. The retriever tool is bound to Qwen:

   ```python
   llm_with_retrieve_tool = self.conversational_agent_llm.bind_tools(
       [create_retreiver_tool(self.retrieve_as_tool)]
   )
   ```

2. Qwen receives these messages:
   ```python
   [
       SystemMessage(content=NHS_RETRIEVER_TOOL_PROMPT),
       HumanMessage(content="I have fever and a cough since last week"),
   ]
   ```

### System prompt sent to Qwen

```
You are a helpful clinical AI assistant deployed in the United Kingdom

You are provided a tool that can retrieve context from a knowledge base taken
from NHS condition web pages which provide information about various medical
conditions.
You should always use the tool to find relevant information to answer the
patient's question rather than relying on your own knowledge.
If you are confused or unsure about the user's question, you should use the
tool to find relevant information or ask the user for more information or ask
further details about their symptoms.
For follow up questions from the user, you should always use the tool to find
new relevant information to answer the user's question given the conversation
history.
You should only not use the tool in very simple messages that do not require
any context like "Hello" or "Thank you", or when the user is just writing
something random.

You can also ask the user for more information or ask further details about
their symptoms.
If you are going to reply to the user, always conclude with a question to
keep the conversation going to help the user or ask for more details about
their symptoms.
In your response, only reply in English and always refer to the user in the
second person.

Decide to use the tool at the start. Do not use the tool after you have already
started your response.
```

### Expected output

Since the query is a medical symptom description, Qwen will decide to use the retriever tool. It returns an `AIMessage` with `tool_calls`:

```python
AIMessage(
    content="",
    tool_calls=[
        {
            "name": "retrieve_as_tool",
            "args": {"query": "fever and cough for a week"},
            "id": "call_abc123",
        }
    ],
)
```

> **Note:** Qwen reformulates the user's query into a better retrieval query. The exact wording may vary, but it extracts the key symptoms.

### State update

```python
return {"messages": [response]}
# → appends the AIMessage with tool_calls to state["messages"]
```

### LangGraph routing

The `tools_condition` checks if the response has tool calls → **YES** → routes to `tools` node.

---

## Step 2 — `tools` (Retriever Execution)

**Component:** LangGraph `ToolNode` wrapping `RAG.retrieve_as_tool()`  
**Infrastructure:** ChromaDB vector store (local, `nhs-use-case-db/`)

### What happens

The ToolNode executes `retrieve_as_tool(query="fever and cough for a week")`.

1. The query is embedded and sent to the Chroma vector store
2. The retriever finds the k=5 most similar NHS condition parent documents
3. Each document has sub-documents with similarity scores

### Expected return (type: `tuple[str, dict]`)

```python
(
    # First element: serialised string for the tool message content
    "Source: {'source': 'flu', 'sub_docs': [...]}\nContent: Flu symptoms include a sudden high temperature, body aches, exhaustion, dry cough, sore throat...\n\n"
    "Source: {'source': 'common-cold', 'sub_docs': [...]}\nContent: Cold symptoms include a gradual onset of a blocked/runny nose, sneezing, sore throat...\n\n"
    "Source: {'source': 'cough', 'sub_docs': [...]}\nContent: Symptoms of a cough include persistent coughing, possibly with mucus, chest pain...\n\n"
    "Source: {'source': 'fever-in-children', 'sub_docs': [...]}\nContent: Children with a high temperature (fever) of 38°C or more...\n\n"
    "Source: {'source': 'coughing-up-blood', 'sub_docs': [...]}\nContent: Coughing up blood can result from various causes...",

    # Second element: artifact dict
    {
        "query": "fever and cough for a week",
        "context": [
            Document(page_content="Flu symptoms include a sudden high temperature...", metadata={"source": "flu", "sub_docs": [Document(metadata={"score": 0.187})]}),
            Document(page_content="Cold symptoms include a gradual onset...", metadata={"source": "common-cold", "sub_docs": [Document(metadata={"score": 0.234})]}),
            Document(page_content="Symptoms of a cough include persistent...", metadata={"source": "cough", "sub_docs": [Document(metadata={"score": 0.298})]}),
            Document(page_content="Children with a high temperature...", metadata={"source": "fever-in-children", "sub_docs": [Document(metadata={"score": 0.412})]}),
            Document(page_content="Coughing up blood can result from...", metadata={"source": "coughing-up-blood", "sub_docs": [Document(metadata={"score": 0.523})]}),
        ],
    }
)
```

### State update

The ToolNode adds a `ToolMessage` to `state["messages"]`:

```python
ToolMessage(
    content="Source: {'source': 'flu', ...}\nContent: Flu symptoms include...\n\n...",
    tool_call_id="call_abc123",
    artifact={
        "query": "fever and cough for a week",
        "context": [Document(...), Document(...), Document(...), Document(...), Document(...)],
    },
)
```

---

## Step 3 — `process_tool_response`

**Component:** `build_rag.py → RAG.process_tool_response()`  
**LLM:** None (pure data extraction)

### What happens

Extracts the query and retrieved documents from the most recent `ToolMessage`'s `artifact`:

```python
query = "fever and cough for a week"
context = [Document(flu), Document(common-cold), Document(cough), Document(fever-in-children), Document(coughing-up-blood)]
```

### Expected return

```python
{
    "context": [
        [  # list of 5 Documents
            Document(page_content="Flu symptoms include...", metadata={"source": "flu", "sub_docs": [...]}),
            Document(page_content="Cold symptoms include...", metadata={"source": "common-cold", "sub_docs": [...]}),
            Document(page_content="Symptoms of a cough include...", metadata={"source": "cough", "sub_docs": [...]}),
            Document(page_content="Children with a high temperature...", metadata={"source": "fever-in-children", "sub_docs": [...]}),
            Document(page_content="Coughing up blood can result...", metadata={"source": "coughing-up-blood", "sub_docs": [...]}),
        ]
    ],
    "retriever_queries": ["fever and cough for a week"],
}
```

---

## Step 4 — `generate` (T0 Clinical Reasoning)

**Component:** `build_rag.py → RAG.generate()`  
**LLM:** T0-1.1-k5-32B (port 8010) — `self.llm` (OpenAI completion endpoint, budget forcing)

This is the most complex step. It has several sub-stages.

### 4a. `obtain_context_and_sources()`

Formats the retrieved documents into a text block with sources and similarity scores:

```python
{
    "serialised_docs": """
Source: flu, similarity score: 0.187. Content:
Flu symptoms include a sudden high temperature, body aches, exhaustion, dry cough, sore throat, headache, difficulty sleeping, loss of appetite, diarrhea, vomiting, and in children, ear pain and reduced activity. If symptoms persist for over seven days or if you're in a high-risk group (elderly, pregnant, with long-term conditions, or a weakened immune system), seek urgent medical advice. Immediate medical attention is needed for sudden chest pain, difficulty breathing, or coughing up blood.

Source: common-cold, similarity score: 0.234. Content:
Cold symptoms include a gradual onset of a blocked/runny nose, sneezing, sore throat, hoarse voice, cough, fatigue, possibly fever, aching muscles, loss of taste/smell, and ear/face pressure. For persistent symptoms lasting over 10 days, worsening conditions, or additional severe symptoms like high fever or difficulty breathing, consult a GP. Otherwise, manage symptoms at home with rest, hydration, and over-the-counter remedies suggested by a pharmacist, avoiding antibiotics which are ineffective against viral infections.

Source: cough, similarity score: 0.298. Content:
Symptoms of a cough include persistent coughing, possibly with mucus, chest pain, difficulty breathing, coughing up blood, and swollen glands in the neck. If symptoms last longer than 3 weeks, worsen rapidly, or are accompanied by unexpected weight loss, chest pain, or other severe signs, seek medical advice from a GP or NHS 111 urgently. Self-care includes resting, staying hydrated, and avoiding contact with others if feeling unwell, while pharmacists can advise on over-the-counter remedies like cough syrups and sweets that may alleviate symptoms but not cure the cough.

Source: fever-in-children, similarity score: 0.412. Content:
Children with a high temperature (fever) of 38°C or more may feel hotter, sweaty, unwell, and could experience seizures. Use a digital thermometer placed in the armpit to measure temperature accurately. Manage fever at home with fluids, regular checks, and paracetamol/ibuprofen if needed; avoid cooling methods like sponging or overdressing. Seek urgent medical advice for infants under 3 months with fever, those 3-6 months with a temperature of 39°C or higher, or if fever persists for more than 5 days, worsens, or is accompanied by concerning symptoms like a non-fading rash, difficulty breathing, or dehydration.

Source: coughing-up-blood, similarity score: 0.523. Content:
Coughing up blood can result from various causes including chronic cough, infections like pneumonia or tuberculosis, and bronchiectasis. Seek an urgent GP appointment or contact NHS 111 for spotting blood; call 999 or visit A&E for heavy bleeding, breathing difficulties, rapid heartbeat, or chest/back pain.
Sources and similarity scores (lower is better): [(flu, 0.187), (common-cold, 0.234), (cough, 0.298), (fever-in-children, 0.412), (coughing-up-blood, 0.523)]""",

    "sources": ["flu", "common-cold", "cough", "fever-in-children", "coughing-up-blood"],
}
```

### 4b. Prompt template invocation

The conversational prompt template (`rag_system_prompt_conversational.txt` + `rag_prompt_conversational.txt`) is invoked:

```python
messages_from_prompt = self.prompt.invoke({
    "question": "I have fever and a cough since last week",
    "context": "<serialised_docs above>",
    "demographics": None,
    "sources": ["flu", "common-cold", "cough", "fever-in-children", "coughing-up-blood"],
})
```

This produces a `ChatPromptValue` with two messages:

**SystemMessage:**

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

Source: flu, similarity score: 0.187. Content:
Flu symptoms include a sudden high temperature, body aches, exhaustion, dry cough...
[...all 5 documents as above...]
Sources and similarity scores (lower is better): [(flu, 0.187), (common-cold, 0.234), (cough, 0.298), (fever-in-children, 0.412), (coughing-up-blood, 0.523)]

This is a summary of their demographics:
None
```

**HumanMessage:**

```
I have fever and a cough since last week
```

### 4c. Message assembly for T0

In conversational mode, the code assembles messages by combining:

- The **system message** from the prompt template (containing context + demographics)
- The **conversation history** (human/system/ai messages from state, excluding tool calls)
- Replaces the last human message with the one from the prompt template

At this point the conversation history in `state["messages"]` is:

```
HumanMessage("I have fever and a cough since last week")
AIMessage("", tool_calls=[...])        ← excluded (has tool_calls)
ToolMessage(...)                        ← excluded (type is "tool")
```

So the final message list sent to T0 is:

```python
[
    SystemMessage(content="You are a clinical reasoning model specialising in NHS conditions.\n\n...{context filled in}...{demographics filled in}"),
    HumanMessage(content="I have fever and a cough since last week"),
]
```

### 4d. Budget forcing with `stream_answer=False`

Since `self.conversational` is `True`, budget forcing is called with `stream_answer=False`:

```python
response = self._budget_forcing_invoke(trimmed_messages, config, stream_answer=False)
```

**This is critical:** T0's thinking tokens are streamed to the user, but the answer tokens are suppressed (they go to `router_respond` instead).

#### Tokenizer applies chat template

The messages are converted to a raw prompt using the T0 tokenizer's chat template:

```
<|im_start|>system
You are a clinical reasoning model specialising in NHS conditions.
[...full system prompt with context and demographics...]
<|im_end|>
<|im_start|>user
I have fever and a cough since last week
<|im_end|>
<|im_start|>assistant
```

#### Thinking phase (streamed to user)

Budget forcing appends `<|im_start|>think\n` and starts generating. The thinking tokens are **streamed to the UI** via the `writer()`:

```
<|im_start|>think
The patient reports fever and cough lasting about one week. Let me analyse against
the retrieved conditions.

The closest matching condition is flu (similarity 0.187), which presents with sudden
high temperature, dry cough, body aches, and exhaustion. The patient's symptoms of
fever and cough align well with flu. The duration of about one week is also consistent
with typical flu duration.

Common cold (0.234) also features cough and possible fever, but onset is more gradual
and the primary symptoms are nasal. The patient doesn't mention nasal symptoms.

The cough condition (0.298) is more generic and applies to persistent coughing but
doesn't specifically address fever.

Fever-in-children (0.412) is less relevant as we have no indication the patient is
a child.

Coughing-up-blood (0.523) has the lowest relevance and the patient hasn't mentioned
blood.

Severity assessment: The patient's symptoms have persisted for about a week. According
to the flu guidance, if symptoms persist for over seven days, they should seek urgent
medical advice. This suggests Urgent Primary Care is appropriate.
```

> **Budget forcing mechanics:** If T0 tries to stop thinking early, budget forcing injects "Wait" to encourage further reasoning, up to `num_stop_skips` times or `max_tokens_thinking` tokens.

#### Answer phase (suppressed, NOT streamed)

Budget forcing then appends `\n<|im_start|>answer\n` and generates the answer. Because `stream_answer=False`:

- The `writer()` calls for `\n<|im_start|>answer\n` are **skipped**
- The `writer()` calls for answer tokens are **skipped**
- The finish signal `writer()` is **skipped**
- But the tokens are still collected into `output`

T0 generates its structured clinical answer:

```
Based on the analysis, the patient's symptoms of fever and persistent cough for
approximately one week are most consistent with influenza (flu). The high similarity
to the flu condition page and the symptom profile — sudden high temperature combined
with dry cough — strongly support this assessment.

Given that symptoms have persisted for over seven days, this warrants medical review
as per NHS guidance.

(flu, Urgent Primary Care)
```

#### Full T0 output (returned as AIMessage)

The complete `response.content` contains both thinking and answer:

```
<|im_start|>think
The patient reports fever and cough lasting about one week...
[...full reasoning...]

<|im_start|>answer
Based on the analysis, the patient's symptoms of fever and persistent cough...
(flu, Urgent Primary Care)
```

### 4e. Generate return value

In conversational mode, `generate` does **NOT** add T0's output to `messages`. Instead it stores it in `t0_reasoning`:

```python
return {
    "system_messages": [SystemMessage(content="You are a clinical reasoning model...")],
    "t0_reasoning": ["<|im_start|>think\nThe patient reports fever and cough...\n<|im_start|>answer\nBased on the analysis...(flu, Urgent Primary Care)"],
    "rag_input_messages": [HumanMessage(content="I have fever and a cough since last week")],
}
```

> **Key design point:** T0's raw clinical reasoning is NOT added to `state["messages"]` — it never enters the conversation history that the user can retrieve via `/get_history`.

---

## Step 5 — `router_respond` (Qwen produces patient-friendly response)

**Component:** `build_rag.py → RAG.router_respond()`  
**LLM:** Qwen 2.5-32B-Instruct (port 8020) — `self.conversational_agent_llm`

### 5a. Read T0's reasoning

```python
t0_output = state["t0_reasoning"][-1]
# = "<|im_start|>think\nThe patient reports...\n<|im_start|>answer\nBased on the analysis...(flu, Urgent Primary Care)"
```

### 5b. Build conversation history (filter)

The router gets the conversation history, excluding tool-call messages:

```python
conversation_history = [
    message for message in state["messages"]
    if message.type in ("human", "ai")
    and not getattr(message, "tool_calls", None)
]
```

At this point, the only qualifying message is:

```python
[HumanMessage(content="I have fever and a cough since last week")]
```

(The AIMessage with tool_calls is excluded.)

### 5c. Assemble router messages

```python
router_messages = [
    SystemMessage(content=ROUTER_RESPONSE_PROMPT),
    HumanMessage(content="I have fever and a cough since last week"),
    HumanMessage(content="Clinical analysis:\n\n<|im_start|>think\nThe patient reports fever and cough lasting about one week...\n<|im_start|>answer\nBased on the analysis...(flu, Urgent Primary Care)"),
]
```

**The ROUTER_RESPONSE_PROMPT sent to Qwen:**

```
You are a helpful clinical AI assistant deployed in the United Kingdom.

Our specialist clinical reasoning model has analysed the patient's symptoms
against NHS condition information. The analysis will be provided to you.

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

### 5d. Stream answer marker

Before the router generates, the method writes the answer marker to the stream:

```python
writer((AIMessageChunk("\n<|im_start|>answer\n"), config["metadata"]))
```

This tells the UI: "the reasoning section is over, the visible answer starts now."

### 5e. Stream router response

Qwen generates a patient-friendly response token by token. Each token is streamed via `writer()`:

**Expected Qwen output (example):**

```
I'm sorry to hear you've been feeling unwell. Based on your symptoms — a fever
and cough that have lasted about a week — this sounds like it could be the flu.

The flu typically causes a sudden high temperature, a dry cough, body aches, and
general exhaustion. Most people start to feel better within a week or so, but
since your symptoms have been going on for about a week now, it would be a good
idea to see your GP or visit an urgent care centre as soon as possible, especially
to rule out any complications.

In the meantime, make sure you're resting, drinking plenty of fluids, and you can
take paracetamol or ibuprofen to help manage the fever and aches.

Could you tell me a bit more about your symptoms? For example, have you been
experiencing any body aches, headaches, or difficulty breathing?
```

### 5f. Finish signal

After the last token, the method writes the finish signal:

```python
writer((AIMessageChunk("", response_metadata={"finish_reason": "stop"}), config["metadata"]))
```

### 5g. Router return value

The router's response is added to `state["messages"]` as a regular AIMessage (this IS part of conversation history):

```python
return {
    "messages": [
        AIMessage(content="I'm sorry to hear you've been feeling unwell. Based on your symptoms — a fever and cough that have lasted about a week — this sounds like it could be the flu.\n\nThe flu typically causes...\n\nCould you tell me a bit more about your symptoms?...")
    ]
}
```

---

## Step 6 — Streaming Output (`_query_stream` filter)

**Component:** `build_rag.py → RAG._query_stream()`

The `_query_stream` generator filters and yields tokens from the graph execution. It listens for `stream_mode=["messages", "custom"]` and yields content from specific nodes:

```python
if not finished and metadata.get("langgraph_node") in [
    "generate",          # T0's thinking tokens
    "router_respond",    # answer marker + router tokens
    "query_or_respond",  # (not used in this flow since Qwen used a tool)
]:
    yield message_chunk.content
```

The `finished` flag is set when `response_metadata.get("finish_reason") == "stop"`, preventing any further tokens from being yielded after the stream is complete.

### Complete streamed output (what the user receives)

The user receives this concatenated token stream:

```
<|im_start|>think
The patient reports fever and cough lasting about one week. Let me analyse against
the retrieved conditions.

The closest matching condition is flu (similarity 0.187), which presents with sudden
high temperature, dry cough, body aches, and exhaustion. The patient's symptoms of
fever and cough align well with flu. The duration of about one week is also consistent
with typical flu duration.

Common cold (0.234) also features cough and possible fever, but onset is more gradual
and the primary symptoms are nasal. The patient doesn't mention nasal symptoms.

The cough condition (0.298) is more generic and applies to persistent coughing but
doesn't specifically address fever.

Fever-in-children (0.412) is less relevant as we have no indication the patient is
a child.

Coughing-up-blood (0.523) has the lowest relevance and the patient hasn't mentioned
blood.

Severity assessment: The patient's symptoms have persisted for about a week. According
to the flu guidance, if symptoms persist for over seven days, they should seek urgent
medical advice. This suggests Urgent Primary Care is appropriate.

<|im_start|>answer
I'm sorry to hear you've been feeling unwell. Based on your symptoms — a fever
and cough that have lasted about a week — this sounds like it could be the flu.

The flu typically causes a sudden high temperature, a dry cough, body aches, and
general exhaustion. Most people start to feel better within a week or so, but
since your symptoms have been going on for about a week now, it would be a good
idea to see your GP or visit an urgent care centre as soon as possible, especially
to rule out any complications.

In the meantime, make sure you're resting, drinking plenty of fluids, and you can
take paracetamol or ibuprofen to help manage the fever and aches.

Could you tell me a bit more about your symptoms? For example, have you been
experiencing any body aches, headaches, or difficulty breathing?
```

---

## Step 7 — Frontend Parsing

**Component:** `web/src/lib/types.ts → makeAIEntry()`

The frontend accumulates the streamed tokens into a single string, then calls `makeAIEntry(fullMessage)`.

### Parsing logic

```typescript
const components = message.split("<|im_start|>answer");
// components.length == 2 → has both reasoning and answer

const [reasoning2, answer2] = components;
const [_, reasoning3] = reasoning2.split("<|im_start|>think");
const reasoning = postProcessReasoning(reasoning3); // trims, removes stray tags
const answer = postProcessAnswer(answer2); // trims, removes stray tags
```

### Result `AIChatEntry`

```typescript
{
    role: "ai",
    content: "<p>I'm sorry to hear you've been feeling unwell. Based on your symptoms — a fever and cough that have lasted about a week — this sounds like it could be the flu.</p><p>The flu typically causes...</p><p>Could you tell me a bit more about your symptoms?...</p>",
    reasoning: "<p>The patient reports fever and cough lasting about one week. Let me analyse against the retrieved conditions...</p><p>Severity assessment: The patient's symptoms have persisted for about a week. According to the flu guidance, if symptoms persist for over seven days, they should seek urgent medical advice. This suggests Urgent Primary Care is appropriate.</p>"
}
```

### UI display

- **Main visible area:** The router's patient-friendly response (from `content`)
- **Collapsible "Reasoning" section:** T0's clinical analysis (from `reasoning`)
- The structured prediction `(flu, Urgent Primary Care)` is part of T0's raw output but gets **separated out** — it appears only inside the reasoning section, never in the main answer

---

## Step 8 — Conversation History (what is persisted)

**Component:** `InMemorySaver` checkpointer

After the graph completes, `state["messages"]` for thread `sunny-otter-42` contains:

```python
[
    HumanMessage(content="I have fever and a cough since last week"),
    AIMessage(content="", tool_calls=[{"name": "retrieve_as_tool", "args": {"query": "fever and cough for a week"}, "id": "call_abc123"}]),
    ToolMessage(content="Source: ...", tool_call_id="call_abc123", artifact={...}),
    AIMessage(content="I'm sorry to hear you've been feeling unwell...Could you tell me a bit more about your symptoms?..."),
]
```

**What is NOT in messages:**

- T0's raw reasoning — stored only in `state["t0_reasoning"]` and not exposed via `/get_history`
- The structured prediction `(flu, Urgent Primary Care)` — internal only

When the user calls `GET /get_history?thread_id=sunny-otter-42`, the frontend's `parseChatEntries()` filters this to show:

- The human message
- The AI message from the router (skipping the tool-call AIMessage and ToolMessage)

---

## Summary Table

| Step | Component               | LLM                 | Input type                                                       | Output type                                | Streamed to user? |
| ---- | ----------------------- | ------------------- | ---------------------------------------------------------------- | ------------------------------------------ | ----------------- |
| 0    | `POST /query_stream`    | —                   | `QueryRequest` (JSON)                                            | `StreamingResponse`                        | —                 |
| 1    | `query_or_respond`      | Qwen                | `[SystemMessage, HumanMessage]`                                  | `AIMessage` with `tool_calls`              | No                |
| 2    | `tools` (retriever)     | —                   | `query: str`                                                     | `tuple[str, dict]` → `ToolMessage`         | No                |
| 3    | `process_tool_response` | —                   | `ToolMessage.artifact`                                           | `dict` with `context`, `retriever_queries` | No                |
| 4    | `generate`              | T0 (budget forcing) | `[SystemMessage, HumanMessage]`                                  | `dict` with `t0_reasoning`                 | **Thinking only** |
| 5    | `router_respond`        | Qwen                | `[SystemMessage, conv_history, HumanMessage(clinical analysis)]` | `dict` with `messages: [AIMessage]`        | **Yes (answer)**  |
| 6    | `_query_stream`         | —                   | Graph stream events                                              | `Iterable[str]`                            | Token-by-token    |
| 7    | Frontend `makeAIEntry`  | —                   | Concatenated string                                              | `AIChatEntry{content, reasoning}`          | —                 |
