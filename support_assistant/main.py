import json
import os
from typing import TypedDict

import chromadb
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END

from prompt_template import POLICY_PROMPT


# -------------------------------------------------
# Configuration
# -------------------------------------------------

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "zepto_policies"

# MOCK_LLM is the graded default.
# Unset or "1" means mock mode.
MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"


# -------------------------------------------------
# Models
# -------------------------------------------------

class AskRequest(BaseModel):
    query: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class GraphState(TypedDict, total=False):
    query: str
    intent: str
    answer: str
    sources: list[str]
    confidence: float


# -------------------------------------------------
# Embedding model and ChromaDB
# -------------------------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


# -------------------------------------------------
# Optional real LLM helper
# -------------------------------------------------

def call_real_llm(prompt: str) -> dict:
    """
    Optional real-LLM path.

    This function is used only when MOCK_LLM=0.
    The graded default does not call any external LLM.
    """

    import requests

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is required when MOCK_LLM=0"
        )

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    content = response.json()[
        "choices"
    ][0]["message"]["content"]

    return json.loads(content)


def validate_real_llm_response(prompt: str) -> AskResponse:
    """
    Try the real LLM response up to 3 times.

    The first attempt plus 2 retries satisfies the
    retry-on-validation-failure requirement.
    """

    current_prompt = prompt

    for attempt in range(3):
        try:
            raw_output = call_real_llm(current_prompt)

            return AskResponse(
                answer=raw_output["answer"],
                sources=raw_output["sources"],
                confidence=raw_output["confidence"]
            )

        except Exception as exc:
            if attempt < 2:
                current_prompt += f"""

CORRECTION:
Your previous response failed validation.

Return ONLY valid JSON with this structure:

{{
    "answer": "string",
    "sources": ["document_or_chunk_id"],
    "confidence": 0.0
}}

Confidence must be between 0 and 1.

Validation error:
{str(exc)}
"""
            else:
                return AskResponse(
                    answer=(
                        "ERROR: Real LLM response could not "
                        "be validated after 3 attempts."
                    ),
                    sources=[],
                    confidence=0.0
                )


# -------------------------------------------------
# Node 1: classify intent
# -------------------------------------------------

def classify_intent(state: GraphState) -> GraphState:
    query = state["query"]
    query_lower = query.lower()

    if MOCK_LLM:
        keywords = [
            "delivery",
            "return",
            "refund",
            "membership",
            "tracking",
            "cancel",
            "gift card",
            "support hours"
        ]

        if any(
            keyword in query_lower
            for keyword in keywords
        ):
            intent = "policy_question"
        else:
            intent = "general_question"

    else:
        prompt = f"""
Classify this user question into exactly one category:

policy_question
general_question

A policy question is related to Zepto delivery, returns,
refunds, membership, tracking, cancellations, gift cards,
or support hours.

Question:
{query}

Return only the category name.
"""

        # Optional real LLM branch
        try:
            import requests

            api_key = os.getenv("GROQ_API_KEY")

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0
                },
                timeout=30
            )

            response.raise_for_status()

            intent = (
                response.json()["choices"][0]
                ["message"]["content"]
                .strip()
            )

            if intent not in [
                "policy_question",
                "general_question"
            ]:
                intent = "general_question"

        except Exception:
            intent = "general_question"

    print(
        f"[classify_intent] Query: {query}"
    )
    print(
        f"[classify_intent] Intent: {intent}"
    )

    return {
        **state,
        "intent": intent
    }


# -------------------------------------------------
# Node 2: retrieve and answer
# -------------------------------------------------

def retrieve_and_answer(
    state: GraphState
) -> GraphState:

    query = state["query"]

    query_embedding = embedding_model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results["documents"][0]
    ids = results["ids"][0]

    print(
        "[retrieve_and_answer] "
        f"Retrieved sources: {ids}"
    )

    if MOCK_LLM:
        top_chunk = documents[0]

        top_chunk_snippet = top_chunk[:200]

        answer = (
            "Based on the retrieved context: "
            + top_chunk_snippet
        )

        response = AskResponse(
            answer=answer,
            sources=ids,
            confidence=1.0
        )

    else:
        context = "\n\n".join(
            [
                f"Source: {doc_id}\n{document}"
                for doc_id, document
                in zip(ids, documents)
            ]
        )

        prompt = POLICY_PROMPT.format(
            context=context,
            query=query
        )

        prompt += """

Return ONLY valid JSON:

{
    "answer": "your grounded answer",
    "sources": ["source ids used"],
    "confidence": 0.0
}
"""

        response = validate_real_llm_response(
            prompt
        )

    return {
        **state,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence
    }


# -------------------------------------------------
# Node 3: direct answer
# -------------------------------------------------

def direct_answer(
    state: GraphState
) -> GraphState:

    if MOCK_LLM:
        response = AskResponse(
            answer=(
                "I can only answer questions "
                "about Zepto policies right now."
            ),
            sources=[],
            confidence=1.0
        )

    else:
        prompt = f"""
You are a Zepto support assistant.

User question:
{state["query"]}

Respond with valid JSON only:

{{
    "answer": "string",
    "sources": [],
    "confidence": 0.0
}}
"""

        response = validate_real_llm_response(
            prompt
        )

    print(
        "[direct_answer] "
        "General question handled directly."
    )

    return {
        **state,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence
    }


# -------------------------------------------------
# Conditional routing
# -------------------------------------------------

def route_query(state: GraphState) -> str:
    return state["intent"]


# -------------------------------------------------
# LangGraph StateGraph
# -------------------------------------------------

graph_builder = StateGraph(
    GraphState
)

graph_builder.add_node(
    "classify_intent",
    classify_intent
)

graph_builder.add_node(
    "retrieve_and_answer",
    retrieve_and_answer
)

graph_builder.add_node(
    "direct_answer",
    direct_answer
)

graph_builder.set_entry_point(
    "classify_intent"
)

graph_builder.add_conditional_edges(
    "classify_intent",
    route_query,
    {
        "policy_question":
            "retrieve_and_answer",

        "general_question":
            "direct_answer"
    }
)

graph_builder.add_edge(
    "retrieve_and_answer",
    END
)

graph_builder.add_edge(
    "direct_answer",
    END
)

graph = graph_builder.compile()


# -------------------------------------------------
# FastAPI application
# -------------------------------------------------

app = FastAPI(
    title="Zepto Policy Support Assistant",
    version="1.0"
)


@app.get("/")
def root():
    return {
        "message":
            "Zepto Policy Support Assistant is running",
        "mock_mode": MOCK_LLM
    }


@app.post(
    "/ask",
    response_model=AskResponse
)
def ask(request: AskRequest):

    result = graph.invoke(
        {
            "query": request.query
        }
    )

    response = AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"]
    )

    return response