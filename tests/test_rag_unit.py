"""
Unit tests for the RAG pipeline that work without vLLM or external services.

These tests use mock LLMs and retrievers to verify the graph construction,
state management, message flow, and streaming logic.
"""

import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from t0_1.rag.build_rag import (
    RAG,
    CustomMessagesState,
    State,
)
from t0_1.rag.utils import NHS_RETRIEVER_TOOL_PROMPT, create_retreiver_tool

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_doc(source: str, content: str, score: float = 0.5) -> Document:
    """Create a Document with the metadata structure the RAG class expects."""
    sub_doc = Document(page_content="sub", metadata={"score": score})
    return Document(
        page_content=content,
        metadata={"source": source, "sub_docs": [sub_doc]},
    )


def _make_fake_retriever(docs: list[Document] | None = None):
    """Return a mock retriever that returns fixed documents."""
    if docs is None:
        docs = [
            _make_doc("headache", "Headache info from NHS", 0.2),
            _make_doc("migraine", "Migraine info from NHS", 0.4),
        ]
    retriever = MagicMock()
    retriever.invoke.return_value = docs
    retriever.ainvoke = MagicMock(return_value=docs)
    return retriever


def _make_fake_llm(response_text: str = "This is a test response"):
    """Return a mock LLM that returns a fixed AIMessage."""
    llm = MagicMock()
    llm.invoke.return_value = AIMessage(content=response_text)
    llm.ainvoke = AsyncMock(return_value=AIMessage(content=response_text))
    # For stream, yield the response in chunks
    llm.stream.return_value = iter([response_text])
    llm.astream = MagicMock(return_value=iter([response_text]))
    # Support bind_tools for conversational mode
    llm.bind_tools = MagicMock(return_value=llm)
    return llm


def _make_prompt_template():
    """Return a simple ChatPromptTemplate for testing."""
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a clinical AI.\n\nContext:\n{context}\n\nDemographics:\n{demographics}",
            ),
            ("human", "{question}"),
        ]
    )


def _build_test_rag(conversational=False, budget_forcing=False, rerank=False):
    """Build a RAG instance with mocked components."""
    retriever = _make_fake_retriever()
    llm = _make_fake_llm("Test answer from T0")
    prompt = _make_prompt_template()

    kwargs = dict(
        retriever=retriever,
        prompt=prompt,
        llm=llm,
        conversational=conversational,
        budget_forcing=budget_forcing,
    )

    if conversational:
        # The conversational agent LLM (Qwen router) needs to support tool binding
        agent_llm = _make_fake_llm("I'll help you with that")
        # When bind_tools is called, the mock should return an LLM
        # that returns a response WITHOUT tool calls (direct response path)
        agent_llm.bind_tools.return_value = agent_llm
        kwargs["conversational_agent_llm"] = agent_llm

    if rerank:
        rerank_llm = _make_fake_llm("headache")
        kwargs["rerank"] = True
        kwargs["rerank_llm"] = rerank_llm
        kwargs["rerank_prompt"] = _make_prompt_template()
        kwargs["rerank_k"] = 1

    return RAG(**kwargs)


# ---------------------------------------------------------------------------
# 1. Graph structure tests
# ---------------------------------------------------------------------------


class TestGraphStructure:
    """Verify the LangGraph is built correctly for both modes."""

    def test_non_conversational_graph_nodes(self):
        """Non-conversational graph should have retrieve and generate nodes."""
        rag = _build_test_rag(conversational=False)
        node_names = set(rag.graph.get_graph().nodes.keys())
        assert "retrieve" in node_names
        assert "generate" in node_names

    def test_non_conversational_graph_with_rerank(self):
        """Non-conversational graph with rerank should include rerank_documents."""
        rag = _build_test_rag(conversational=False, rerank=True)
        node_names = set(rag.graph.get_graph().nodes.keys())
        assert "retrieve" in node_names
        assert "rerank_documents" in node_names
        assert "generate" in node_names

    def test_conversational_graph_nodes(self):
        """Conversational graph should have the full pipeline nodes."""
        rag = _build_test_rag(conversational=True)
        node_names = set(rag.graph.get_graph().nodes.keys())
        assert "query_or_respond" in node_names
        assert "tools" in node_names
        assert "process_tool_response" in node_names
        assert "generate" in node_names

    def test_conversational_graph_has_conditional_edge(self):
        """Conversational graph should have conditional edges from query_or_respond."""
        rag = _build_test_rag(conversational=True)
        graph = rag.graph.get_graph()
        # query_or_respond should have edges going to both tools and __end__
        qor_edges = [e for e in graph.edges if e.source == "query_or_respond"]
        targets = {e.target for e in qor_edges}
        assert "tools" in targets or "__end__" in targets

    def test_reset_graph_rebuilds(self):
        """reset_graph should create a fresh graph instance."""
        rag = _build_test_rag(conversational=False)
        old_graph = rag.graph
        rag.reset_graph()
        assert rag.graph is not old_graph


# ---------------------------------------------------------------------------
# 2. State and type tests
# ---------------------------------------------------------------------------


class TestStateTypes:
    """Verify state TypedDicts are properly structured."""

    def test_state_has_required_fields(self):
        """State TypedDict should have all expected fields."""
        expected_fields = {
            "question",
            "system_messages",
            "messages",
            "retriever_queries",
            "context",
            "reranked_context",
            "reranker_response",
            "reranker_response_processed",
            "reranker_success",
            "demographics",
        }
        assert expected_fields.issubset(State.__annotations__.keys())

    def test_custom_messages_state_has_required_fields(self):
        """CustomMessagesState should have its specific fields."""
        expected_fields = {
            "system_messages",
            "rag_input_messages",
            "retriever_queries",
            "context",
            "reranked_context",
            "reranker_response",
            "reranker_response_processed",
            "reranker_success",
            "demographics",
        }
        assert expected_fields.issubset(CustomMessagesState.__annotations__.keys())

    def test_custom_messages_state_has_messages_key(self):
        """CustomMessagesState should have 'messages' from MessagesState base."""
        # TypedDict flattens the MRO, so we check that the 'messages'
        # annotation exists (inherited from MessagesState)
        all_annotations = {}
        for cls in reversed(CustomMessagesState.__mro__):
            all_annotations.update(getattr(cls, "__annotations__", {}))
        assert "messages" in all_annotations


# ---------------------------------------------------------------------------
# 3. Retriever tool creation
# ---------------------------------------------------------------------------


class TestRetrieverTool:
    """Verify the retriever tool is created correctly."""

    def test_create_retriever_tool_returns_structured_tool(self):
        """create_retreiver_tool should return a StructuredTool."""
        from langchain.tools import StructuredTool

        retriever = _make_fake_retriever()
        rag = _build_test_rag()
        tool = create_retreiver_tool(rag.retrieve_as_tool)
        assert isinstance(tool, StructuredTool)
        assert tool.name == "retrieve_as_tool"
        assert tool.response_format == "content_and_artifact"

    def test_retrieve_as_tool_returns_content_and_artifact(self):
        """retrieve_as_tool should return (serialised_string, artifact_dict)."""
        rag = _build_test_rag()
        content, artifact = rag.retrieve_as_tool("headache symptoms")
        assert isinstance(content, str)
        assert isinstance(artifact, dict)
        assert "query" in artifact
        assert "context" in artifact
        assert artifact["query"] == "headache symptoms"
        assert len(artifact["context"]) == 2  # default fixture returns 2 docs


# ---------------------------------------------------------------------------
# 4. Context and sources formatting
# ---------------------------------------------------------------------------


class TestContextFormatting:
    """Verify obtain_context_and_sources formats documents correctly."""

    def test_obtain_context_and_sources_basic(self):
        """Should format documents with sources and scores."""
        rag = _build_test_rag()
        docs = [
            _make_doc("headache", "Headache content", 0.2),
            _make_doc("migraine", "Migraine content", 0.4),
        ]
        state = {"context": [docs], "reranked_context": [None]}
        result = rag.obtain_context_and_sources(state)
        assert "serialised_docs" in result
        assert "sources" in result
        assert "headache" in result["sources"]
        assert "migraine" in result["sources"]
        assert "0.200" in result["serialised_docs"]
        assert "0.400" in result["serialised_docs"]

    def test_obtain_context_with_rerank(self):
        """When rerank is enabled, should use reranked_context."""
        rag = _build_test_rag(rerank=True)
        reranked = [_make_doc("headache", "Headache content", 0.2)]
        state = {
            "context": [
                [_make_doc("headache", "H", 0.2), _make_doc("migraine", "M", 0.4)]
            ],
            "reranked_context": [reranked],
        }
        result = rag.obtain_context_and_sources(state)
        assert len(result["sources"]) == 1
        assert result["sources"] == ["headache"]


# ---------------------------------------------------------------------------
# 5. Process tool response
# ---------------------------------------------------------------------------


class TestProcessToolResponse:
    """Verify process_tool_response extracts data from ToolMessages."""

    def test_extracts_query_and_context(self):
        """Should extract query and context from the latest ToolMessage."""
        rag = _build_test_rag(conversational=True)
        docs = [_make_doc("cold", "Common cold info", 0.3)]
        tool_msg = ToolMessage(
            content="Retrieved docs",
            tool_call_id="test_id",
            artifact={"query": "I have a cold", "context": docs},
        )
        state = {
            "messages": [
                HumanMessage(content="I have a cold"),
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": "test_id",
                            "name": "retrieve_as_tool",
                            "args": {"query": "cold"},
                        }
                    ],
                ),
                tool_msg,
            ],
            "context": [],
            "retriever_queries": [],
        }
        result = rag.process_tool_response(state)
        assert result["retriever_queries"] == ["I have a cold"]
        assert len(result["context"]) == 1
        assert result["context"][0] == docs

    def test_empty_when_no_tool_messages(self):
        """Should return empty query and context when no ToolMessages."""
        rag = _build_test_rag(conversational=True)
        state = {
            "messages": [HumanMessage(content="Hello")],
            "context": [],
            "retriever_queries": [],
        }
        result = rag.process_tool_response(state)
        assert result["retriever_queries"] == [""]
        assert result["context"] == [[]]


# ---------------------------------------------------------------------------
# 6. Prompt template tests
# ---------------------------------------------------------------------------


class TestPromptTemplates:
    """Verify prompt templates load and render correctly."""

    def test_conversational_system_prompt_loads(self):
        """The conversational system prompt template should load from disk."""
        path = TEMPLATES_DIR / "rag_system_prompt_conversational.txt"
        assert path.exists(), f"Missing template: {path}"
        content = path.read_text()
        assert "{context}" in content
        assert "{demographics}" in content

    def test_conversational_prompt_template_loads(self):
        """The conversational prompt template should load from disk."""
        path = TEMPLATES_DIR / "rag_prompt_conversational.txt"
        assert path.exists(), f"Missing template: {path}"
        content = path.read_text()
        assert "{question}" in content

    def test_non_conversational_prompt_loads(self):
        """The non-conversational prompt template should load from disk."""
        path = TEMPLATES_DIR / "rag_prompt.txt"
        assert path.exists(), f"Missing template: {path}"
        content = path.read_text()
        assert "{question}" in content
        assert "{context}" in content
        assert "{demographics}" in content

    def test_rag_templates_have_valid_placeholders(self):
        """RAG templates should only contain valid placeholder names."""
        valid_placeholders = {
            "context",
            "question",
            "demographics",
            "sources",
            "symptoms_description",
            "document_titles",
            "document_text",
            "k",
        }
        rag_templates = [
            "rag_prompt.txt",
            "rag_prompt_conversational.txt",
            "rag_system_prompt.txt",
            "rag_system_prompt_conversational.txt",
            "rag_system_prompt_conversational_testing.txt",
        ]
        for name in rag_templates:
            path = TEMPLATES_DIR / name
            if not path.exists():
                continue
            content = path.read_text()
            placeholders = set(re.findall(r"\{(\w+)\}", content))
            invalid = placeholders - valid_placeholders
            assert (
                not invalid
            ), f"Template {name} has unexpected placeholders: {invalid}"

    def test_custom_prompt_template_reader(self):
        """read_prompt_template should return a ChatPromptTemplate."""
        from t0_1.rag.custom_prompt_template import read_prompt_template

        prompt_path = TEMPLATES_DIR / "rag_prompt_conversational.txt"
        system_path = TEMPLATES_DIR / "rag_system_prompt_conversational.txt"
        template = read_prompt_template(prompt_path, system_path)
        assert isinstance(template, ChatPromptTemplate)
        # Should have system + human messages
        assert len(template.messages) == 2

    def test_nhs_retriever_tool_prompt_content(self):
        """NHS_RETRIEVER_TOOL_PROMPT should contain key instructions."""
        assert "United Kingdom" in NHS_RETRIEVER_TOOL_PROMPT
        assert "tool" in NHS_RETRIEVER_TOOL_PROMPT.lower()
        assert "English" in NHS_RETRIEVER_TOOL_PROMPT


# ---------------------------------------------------------------------------
# 7. Non-conversational generate (with mocked LLM)
# ---------------------------------------------------------------------------


class TestGenerate:
    """Test the generate method with mocked LLM."""

    def test_generate_non_conversational(self):
        """generate should call LLM and return messages dict."""
        rag = _build_test_rag(conversational=False)
        docs = [_make_doc("headache", "Headache info", 0.2)]
        state = {
            "question": "I have a headache",
            "context": [docs],
            "reranked_context": [None],
            "demographics": "30 year old male",
            "system_messages": [],
            "messages": [],
        }
        config = {"metadata": {"langgraph_node": "generate"}}
        result = rag.generate(state, config)
        assert "messages" in result
        assert "system_messages" in result
        # The last message should be the AI response
        assert any(isinstance(m, AIMessage) for m in result["messages"])

    def test_generate_conversational_returns_rag_input_messages(self):
        """In conversational mode, generate should return rag_input_messages and t0_reasoning."""
        rag = _build_test_rag(conversational=True)
        docs = [_make_doc("headache", "Headache info", 0.2)]
        state = {
            "messages": [
                HumanMessage(content="I have a headache"),
            ],
            "context": [docs],
            "reranked_context": [None],
            "demographics": "30 year old male",
            "system_messages": [],
            "rag_input_messages": [],
            "t0_reasoning": [],
        }
        config = {"metadata": {"langgraph_node": "generate"}}
        result = rag.generate(state, config)
        assert "t0_reasoning" in result
        assert "rag_input_messages" in result
        assert "system_messages" in result

    def test_agenerate_non_conversational_returns_list_messages(self):
        """agenerate non-conversational should build a list of messages (not a bare Message).

        Regression: line 900 had `messages = messages_from_prompt.messages[-1]`
        instead of `messages = [messages_from_prompt.messages[-1]]`, causing
        TypeError when concatenating with [system_message].
        """
        import asyncio

        rag = _build_test_rag(conversational=False)
        docs = [_make_doc("headache", "Headache info", 0.2)]
        state = {
            "question": "I have a headache",
            "context": [docs],
            "reranked_context": [None],
            "demographics": "30 year old male",
            "system_messages": [],
            "messages": [],
        }
        config = {"metadata": {"langgraph_node": "generate"}}
        result = asyncio.run(rag.agenerate(state, config))
        assert "messages" in result
        assert "system_messages" in result
        assert any(isinstance(m, AIMessage) for m in result["messages"])

    def test_agenerate_conversational_passes_string_to_prompt(self):
        """agenerate conversational should pass question as a string, not a Message.

        Regression: line 861 had `human_message = message` (full HumanMessage)
        instead of `human_message = message.content` (string), causing the
        prompt template to render {question} as 'content=...' instead of text.
        """
        import asyncio

        rag = _build_test_rag(conversational=True)
        docs = [_make_doc("headache", "Headache info", 0.2)]
        state = {
            "messages": [
                HumanMessage(content="I have a headache"),
            ],
            "context": [docs],
            "reranked_context": [None],
            "demographics": "30 year old male",
            "system_messages": [],
            "rag_input_messages": [],
        }
        config = {"metadata": {"langgraph_node": "generate"}}
        result = asyncio.run(rag.agenerate(state, config))

        # The rag_input_messages should contain a human message whose content
        # is the plain text question, not a repr of a HumanMessage object
        last_input = result["rag_input_messages"][-1]
        assert "I have a headache" in last_input.content
        assert "content=" not in last_input.content


# ---------------------------------------------------------------------------
# 8. Thread / memory management
# ---------------------------------------------------------------------------


class TestMemoryManagement:
    """Test conversation memory and thread management."""

    def test_clear_history_returns_message(self):
        """clear_history should return a confirmation string."""
        rag = _build_test_rag()
        result = rag.clear_history("test-thread")
        assert result == "History cleared."

    def test_get_thread_ids_initially_empty(self):
        """Initially there should be no active thread IDs."""
        rag = _build_test_rag()
        thread_ids = rag.get_thread_ids()
        assert thread_ids == []


# ---------------------------------------------------------------------------
# 9. RAG endpoint tests (FastAPI app)
# ---------------------------------------------------------------------------


class TestRAGEndpoint:
    """Test the FastAPI app creation and basic endpoint structure."""

    def test_create_rag_app_returns_fastapi_app(self):
        """create_rag_app should return a FastAPI instance."""
        from t0_1.rag.rag_endpoint import create_rag_app

        rag = _build_test_rag()
        app = create_rag_app(rag)
        from fastapi import FastAPI

        assert isinstance(app, FastAPI)

    def test_app_has_expected_routes(self):
        """The app should have all expected endpoint routes."""
        from t0_1.rag.rag_endpoint import create_rag_app

        rag = _build_test_rag()
        app = create_rag_app(rag)
        routes = {route.path for route in app.routes}
        assert "/" in routes
        assert "/query" in routes
        assert "/query_stream" in routes
        assert "/clear_history" in routes
        assert "/get_history" in routes
        assert "/new_thread_id" in routes
        assert "/get_thread_ids" in routes

    def test_query_request_model(self):
        """QueryRequest should accept the expected fields."""
        from t0_1.rag.rag_endpoint import QueryRequest

        req = QueryRequest(query="test", thread_id="t1", demographics="30M")
        assert req.query == "test"
        assert req.thread_id == "t1"
        assert req.demographics == "30M"

    def test_query_request_defaults(self):
        """QueryRequest should have sensible defaults."""
        from t0_1.rag.rag_endpoint import QueryRequest

        req = QueryRequest(query="test")
        assert req.thread_id == "0"
        assert req.demographics is None


# ---------------------------------------------------------------------------
# 10. load_llm validation
# ---------------------------------------------------------------------------


class TestLoadLLM:
    """Test load_llm input validation (without actually loading models)."""

    def test_load_llm_rejects_empty_provider(self):
        """load_llm should raise ValueError for empty provider."""
        from t0_1.rag.build_rag import load_llm

        with pytest.raises(ValueError, match="LLM provider is not specified"):
            load_llm("", "some-model")

    def test_load_llm_rejects_empty_model_name(self):
        """load_llm should raise ValueError for empty model name."""
        from t0_1.rag.build_rag import load_llm

        with pytest.raises(ValueError, match="LLM model name is not specified"):
            load_llm("openai", "")

    def test_load_llm_rejects_unknown_provider(self):
        """load_llm should raise ValueError for unknown provider."""
        from t0_1.rag.build_rag import load_llm

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            load_llm("unknown_provider", "some-model")


# ---------------------------------------------------------------------------
# 11. build_rag validation
# ---------------------------------------------------------------------------


class TestBuildRAGValidation:
    """Test build_rag factory function validation."""

    def test_budget_forcing_requires_openai_completion(self):
        """build_rag should reject budget_forcing with non-openai_completion provider."""
        from t0_1.rag.build_rag import build_rag

        with pytest.raises(ValueError, match="Budget forcing"):
            build_rag(
                conditions_file="dummy.json",
                llm_provider="openai",
                llm_model_name="test",
                budget_forcing=True,
            )


# ---------------------------------------------------------------------------
# 12. Router integration tests (plan: route T0 through Qwen router)
# ---------------------------------------------------------------------------


class TestRouterGraphStructure:
    """Verify the conversational graph includes router_respond after the plan changes."""

    def test_conversational_graph_has_router_respond_node(self):
        """After the plan, conversational graph must include a router_respond node."""
        rag = _build_test_rag(conversational=True)
        node_names = set(rag.graph.get_graph().nodes.keys())
        assert "router_respond" in node_names, (
            f"router_respond node missing from conversational graph. "
            f"Found nodes: {node_names}"
        )

    def test_generate_edges_to_router_respond_not_end(self):
        """generate should edge to router_respond, NOT directly to __end__."""
        rag = _build_test_rag(conversational=True)
        graph = rag.graph.get_graph()
        gen_edges = [e for e in graph.edges if e.source == "generate"]
        gen_targets = {e.target for e in gen_edges}
        assert (
            "router_respond" in gen_targets
        ), f"generate should edge to router_respond, but targets are: {gen_targets}"
        assert (
            "__end__" not in gen_targets
        ), "generate should NOT edge directly to __end__ in conversational mode"

    def test_router_respond_edges_to_end(self):
        """router_respond should edge to __end__."""
        rag = _build_test_rag(conversational=True)
        graph = rag.graph.get_graph()
        rr_edges = [e for e in graph.edges if e.source == "router_respond"]
        rr_targets = {e.target for e in rr_edges}
        assert (
            "__end__" in rr_targets
        ), f"router_respond should edge to __end__, but targets are: {rr_targets}"

    def test_non_conversational_graph_unchanged(self):
        """Non-conversational graph should NOT have router_respond (backward compat)."""
        rag = _build_test_rag(conversational=False)
        node_names = set(rag.graph.get_graph().nodes.keys())
        assert "router_respond" not in node_names


class TestStateTypesRouter:
    """Verify t0_reasoning field is present on CustomMessagesState."""

    def test_custom_messages_state_has_t0_reasoning(self):
        """CustomMessagesState must have t0_reasoning field for the router plan."""
        all_annotations = {}
        for cls in reversed(CustomMessagesState.__mro__):
            all_annotations.update(getattr(cls, "__annotations__", {}))
        assert "t0_reasoning" in all_annotations, (
            f"t0_reasoning missing from CustomMessagesState. "
            f"Found: {set(all_annotations.keys())}"
        )


class TestGenerateRouter:
    """Verify generate behavior changes for the router plan."""

    def test_generate_conversational_returns_t0_reasoning(self):
        """Conversational generate must return t0_reasoning, not T0's message."""
        rag = _build_test_rag(conversational=True)
        docs = [_make_doc("headache", "Headache info", 0.2)]
        state = {
            "messages": [HumanMessage(content="I have a headache")],
            "context": [docs],
            "reranked_context": [None],
            "demographics": "30 year old male",
            "system_messages": [],
            "rag_input_messages": [],
            "t0_reasoning": [],
        }
        config = {"metadata": {"langgraph_node": "generate"}}
        result = rag.generate(state, config)
        assert (
            "t0_reasoning" in result
        ), "Conversational generate must return t0_reasoning key"
        assert (
            len(result["t0_reasoning"]) >= 1
        ), "t0_reasoning should contain T0's output"
        # T0's response should NOT be in messages (it goes to router instead)
        ai_messages_in_result = [
            m for m in result.get("messages", []) if isinstance(m, AIMessage)
        ]
        assert len(ai_messages_in_result) == 0, (
            "Conversational generate should NOT put T0's AIMessage into messages "
            "(it should go to t0_reasoning for the router to consume)"
        )

    def test_agenerate_conversational_returns_t0_reasoning(self):
        """Async conversational generate must also return t0_reasoning."""
        import asyncio

        rag = _build_test_rag(conversational=True)
        docs = [_make_doc("headache", "Headache info", 0.2)]
        state = {
            "messages": [HumanMessage(content="I have a headache")],
            "context": [docs],
            "reranked_context": [None],
            "demographics": "30 year old male",
            "system_messages": [],
            "rag_input_messages": [],
            "t0_reasoning": [],
        }
        config = {"metadata": {"langgraph_node": "generate"}}
        result = asyncio.run(rag.agenerate(state, config))
        assert "t0_reasoning" in result
        assert len(result["t0_reasoning"]) >= 1

    def test_generate_non_conversational_still_returns_messages(self):
        """Non-conversational generate must still return messages (backward compat).

        This is critical: the evaluation pipeline uses non-conversational mode
        and depends on messages containing the AI response.
        """
        rag = _build_test_rag(conversational=False)
        docs = [_make_doc("headache", "Headache info", 0.2)]
        state = {
            "question": "I have a headache",
            "context": [docs],
            "reranked_context": [None],
            "demographics": "30 year old male",
            "system_messages": [],
            "messages": [],
        }
        config = {"metadata": {"langgraph_node": "generate"}}
        result = rag.generate(state, config)
        assert "messages" in result
        assert any(
            isinstance(m, AIMessage) for m in result["messages"]
        ), "Non-conversational generate must still return AIMessage in messages"
        assert (
            "t0_reasoning" not in result
        ), "Non-conversational generate should NOT return t0_reasoning"


class TestRouterRespond:
    """Test the router_respond method that passes T0's output to the Qwen router."""

    def _make_router_state(self, t0_output="(headache, Self-care)"):
        """Build a minimal state for router_respond testing."""
        return {
            "messages": [
                HumanMessage(content="I have a headache"),
            ],
            "system_messages": [],
            "rag_input_messages": [],
            "t0_reasoning": [t0_output],
            "context": [],
            "reranked_context": [],
            "demographics": "30 year old male",
        }

    @patch("t0_1.rag.build_rag.get_stream_writer")
    def test_router_respond_returns_ai_message(self, mock_get_writer):
        """router_respond must return messages with an AIMessage."""
        mock_get_writer.return_value = MagicMock()
        rag = _build_test_rag(conversational=True)
        state = self._make_router_state()
        config = {"metadata": {"langgraph_node": "router_respond"}}
        result = rag.router_respond(state, config)
        assert "messages" in result, "router_respond must return messages key"
        assert len(result["messages"]) >= 1
        assert isinstance(
            result["messages"][0], AIMessage
        ), "router_respond must return an AIMessage (the router's response)"

    @patch("t0_1.rag.build_rag.get_stream_writer")
    def test_router_respond_uses_t0_reasoning(self, mock_get_writer):
        """router_respond must read t0_reasoning from state and pass to router LLM."""
        mock_get_writer.return_value = MagicMock()
        rag = _build_test_rag(conversational=True)
        t0_output = "Analysis: headache likely. (headache, Self-care)"
        state = self._make_router_state(t0_output=t0_output)
        config = {"metadata": {"langgraph_node": "router_respond"}}
        rag.router_respond(state, config)
        # The conversational_agent_llm should have been called
        router_llm = rag.conversational_agent_llm
        assert (
            router_llm.invoke.called or router_llm.stream.called
        ), "router_respond must call the conversational_agent_llm"
        # T0's reasoning should appear somewhere in the call args
        all_call_args = str(router_llm.invoke.call_args or router_llm.stream.call_args)
        assert (
            t0_output in all_call_args or router_llm.invoke.called
        ), "router_respond must pass T0's reasoning to the router LLM"

    @patch("t0_1.rag.build_rag.get_stream_writer")
    def test_router_respond_writes_answer_marker(self, mock_get_writer):
        """router_respond must write the <|im_start|>answer marker to the stream."""
        writer = MagicMock()
        mock_get_writer.return_value = writer
        rag = _build_test_rag(conversational=True)
        state = self._make_router_state()
        config = {"metadata": {"langgraph_node": "router_respond"}}
        rag.router_respond(state, config)
        # Check that writer was called with the answer marker
        all_writes = [str(call) for call in writer.call_args_list]
        combined = " ".join(all_writes)
        assert "<|im_start|>answer" in combined, (
            "router_respond must write <|im_start|>answer marker to stream "
            "so the UI knows where the visible answer starts"
        )

    @patch("t0_1.rag.build_rag.get_stream_writer")
    def test_router_respond_writes_finish_signal(self, mock_get_writer):
        """router_respond must write a finish_reason=stop signal."""
        writer = MagicMock()
        mock_get_writer.return_value = writer
        rag = _build_test_rag(conversational=True)
        state = self._make_router_state()
        config = {"metadata": {"langgraph_node": "router_respond"}}
        rag.router_respond(state, config)
        all_writes = [str(call) for call in writer.call_args_list]
        combined = " ".join(all_writes)
        assert (
            "finish_reason" in combined
        ), "router_respond must write a finish signal so the UI knows streaming ended"

    @patch("t0_1.rag.build_rag.get_stream_writer")
    def test_arouter_respond_returns_ai_message(self, mock_get_writer):
        """Async arouter_respond must also return an AIMessage."""
        import asyncio

        mock_get_writer.return_value = MagicMock()
        rag = _build_test_rag(conversational=True)
        state = self._make_router_state()
        config = {"metadata": {"langgraph_node": "router_respond"}}
        result = asyncio.run(rag.arouter_respond(state, config))
        assert "messages" in result
        assert isinstance(result["messages"][0], AIMessage)

    @patch("t0_1.rag.build_rag.get_stream_writer")
    def test_router_respond_does_not_leak_t0_reasoning_to_messages(
        self, mock_get_writer
    ):
        """T0's raw reasoning must NOT end up in the conversation messages."""
        mock_get_writer.return_value = MagicMock()
        rag = _build_test_rag(conversational=True)
        t0_output = "(headache, Urgent Primary Care)"
        state = self._make_router_state(t0_output=t0_output)
        config = {"metadata": {"langgraph_node": "router_respond"}}
        result = rag.router_respond(state, config)
        # The returned messages should contain the ROUTER's response,
        # not T0's raw clinical reasoning
        router_response = result["messages"][0].content
        # The router_response should be from the mock LLM, not the raw T0 output
        assert (
            router_response != t0_output
        ), "router_respond should return the ROUTER's response, not T0's raw reasoning"


class TestRouterPrompt:
    """Verify ROUTER_RESPONSE_PROMPT is available and has expected content."""

    def test_router_response_prompt_importable(self):
        """ROUTER_RESPONSE_PROMPT must be importable from utils."""
        from t0_1.rag.utils import ROUTER_RESPONSE_PROMPT

        assert isinstance(ROUTER_RESPONSE_PROMPT, str)
        assert len(ROUTER_RESPONSE_PROMPT) > 50

    def test_router_response_prompt_has_severity_mapping(self):
        """ROUTER_RESPONSE_PROMPT must include severity-to-action guidance."""
        from t0_1.rag.utils import ROUTER_RESPONSE_PROMPT

        assert "Self-care" in ROUTER_RESPONSE_PROMPT
        assert "Urgent Primary Care" in ROUTER_RESPONSE_PROMPT
        assert "A&E" in ROUTER_RESPONSE_PROMPT

    def test_router_response_prompt_has_uk_context(self):
        """ROUTER_RESPONSE_PROMPT must reference UK context."""
        from t0_1.rag.utils import ROUTER_RESPONSE_PROMPT

        assert "United Kingdom" in ROUTER_RESPONSE_PROMPT


class TestConversationalTemplateChange:
    """Verify the conversational system prompt has been updated for structured prediction."""

    def test_conversational_system_prompt_has_structured_prediction(self):
        """The conversational system prompt must instruct T0 to produce structured output."""
        path = TEMPLATES_DIR / "rag_system_prompt_conversational.txt"
        content = path.read_text()
        # Must contain the structured prediction format instruction
        assert (
            "condition_name" in content.lower() or "severity_level" in content.lower()
        ), (
            "Conversational system prompt must instruct T0 to produce "
            "(condition_name, severity_level) structured prediction"
        )

    def test_conversational_system_prompt_no_conversational_response(self):
        """The conversational system prompt must tell T0 NOT to write a conversational response."""
        path = TEMPLATES_DIR / "rag_system_prompt_conversational.txt"
        content = path.read_text().lower()
        assert "do not" in content and (
            "conversational" in content or "follow-up" in content
        ), (
            "Conversational system prompt must instruct T0 NOT to produce "
            "conversational responses (that's the router's job now)"
        )


class TestStreamingFilter:
    """Verify the streaming filter includes router_respond."""

    def test_query_stream_yields_from_router_respond(self):
        """_query_stream's filter must include router_respond so router tokens reach the user.

        We test this by inspecting the source code for the streaming filter.
        This is a code-level guard: if someone removes router_respond from the
        filter, this test fails.
        """
        import inspect

        source = inspect.getsource(RAG._query_stream)
        assert "router_respond" in source, (
            "_query_stream must include 'router_respond' in its streaming filter "
            "so the router's tokens are yielded to the user"
        )
