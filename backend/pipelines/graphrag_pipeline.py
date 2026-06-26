import re
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from services.gemini_service import chat_complete
from services.embedding_service import embed_text
from database.qdrant_client import get_qdrant_client
from database.neo4j_client import get_driver
from config import get_settings

STRUCTURAL_KEYWORDS = [
    "upstream", "downstream", "connected", "shuts down", "trips",
    "depends on", "dependency", "topology", "affects", "causes",
    "what happens if", "what breaks", "linked to", "feeds into",
    "impact", "cascade", "failure", "fault"
]
FACTUAL_KEYWORDS = [
    "spec", "specification", "manual", "procedure", "torque", "pressure",
    "maintenance", "installation", "calibration", "temperature", "rpm",
    "how to", "what is", "describe"
]
TAG_PATTERN = re.compile(r'\b([A-Z]{1,6}-\d{1,4})\b')


class GraphRAGState(TypedDict):
    query: str
    route: Literal["vector", "graph", "hybrid"] | None
    vector_results: list[dict]
    graph_results: list[dict]
    fused_context: str
    answer: str
    sources: list[str]


async def classify_query(state: GraphRAGState) -> GraphRAGState:
    query_lower = state["query"].lower()
    has_structural = any(kw in query_lower for kw in STRUCTURAL_KEYWORDS)
    has_factual = any(kw in query_lower for kw in FACTUAL_KEYWORDS)

    if has_structural and has_factual:
        route = "hybrid"
    elif has_structural:
        route = "graph"
    else:
        route = "vector"

    return {**state, "route": route}


async def retrieve_from_qdrant(state: GraphRAGState) -> GraphRAGState:
    query_vector = await embed_text(state["query"])
    client = await get_qdrant_client()
    settings = get_settings()

    response = await client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_vector,
        limit=5,
        with_payload=True
    )

    vector_results = [
        {
            "chunk_text": r.payload.get("chunk_text", ""),
            "source_file": r.payload.get("source_file", ""),
            "page_number": r.payload.get("page_number"),
            "score": r.score
        }
        for r in response.points
    ]
    return {**state, "vector_results": vector_results}


async def retrieve_from_neo4j(state: GraphRAGState) -> GraphRAGState:
    mentioned_tags = TAG_PATTERN.findall(state["query"].upper())
    driver = await get_driver()
    graph_results = []

    async with driver.session() as session:
        if mentioned_tags:
            for tag in mentioned_tags[:3]:
                result = await session.run(
                    """
                    MATCH (a:Asset {tag_number: $tag})
                    OPTIONAL MATCH (upstream:Asset)-[:CONNECTED_TO]->(a)
                    OPTIONAL MATCH (a)-[:CONNECTED_TO]->(downstream:Asset)
                    OPTIONAL MATCH (a)-[:HAS_OBSERVATION]->(o:KnowledgeObservation)
                    RETURN a,
                           collect(DISTINCT upstream.tag_number) as upstream_assets,
                           collect(DISTINCT downstream.tag_number) as downstream_assets,
                           collect(DISTINCT {issue: o.observed_issue, action: o.mitigation_action}) as observations
                    """,
                    tag=tag
                )
                record = await result.single()
                if record and record["a"]:
                    graph_results.append({
                        "asset": dict(record["a"]),
                        "upstream_assets": [t for t in record["upstream_assets"] if t],
                        "downstream_assets": [t for t in record["downstream_assets"] if t],
                        "observations": [o for o in record["observations"] if o.get("issue")]
                    })
        else:
            result = await session.run(
                """
                MATCH (a:Asset)-[:CONNECTED_TO]->(b:Asset)
                RETURN a.tag_number as source, b.tag_number as target
                LIMIT 20
                """
            )
            async for record in result:
                graph_results.append(dict(record))

    return {**state, "graph_results": graph_results}


async def fuse_context(state: GraphRAGState) -> GraphRAGState:
    context_parts = []
    sources = []

    if state["vector_results"]:
        context_parts.append("=== DOCUMENT KNOWLEDGE ===")
        for r in state["vector_results"]:
            context_parts.append(f"[Source: {r['source_file']}, Page {r['page_number']}]")
            context_parts.append(r["chunk_text"])
            if r["source_file"]:
                sources.append(f"{r['source_file']} (page {r['page_number']})")

    if state["graph_results"]:
        context_parts.append("\n=== ASSET TOPOLOGY & OBSERVATIONS ===")
        for r in state["graph_results"]:
            if "asset" in r:
                a = r["asset"]
                lines = [
                    f"Asset: {a.get('tag_number')} ({a.get('id', '')}) — {a.get('manufacturer', '')} {a.get('model_number', '')}",
                ]
                if r.get("upstream_assets"):
                    lines.append(f"  Feeds FROM (upstream assets that supply this asset): {', '.join(r['upstream_assets'])}")
                if r.get("downstream_assets"):
                    lines.append(f"  Feeds INTO (downstream assets that depend on this asset): {', '.join(r['downstream_assets'])}")
                if not r.get("upstream_assets") and not r.get("downstream_assets"):
                    lines.append("  No connected assets found.")
                for obs in r.get("observations", []):
                    lines.append(f"  Known issue: {obs.get('issue', '')}")
                    if obs.get("action"):
                        lines.append(f"  Resolution: {obs.get('action', '')}")
                context_parts.append("\n".join(lines))
            else:
                context_parts.append(f"  {r.get('source')} --> {r.get('target')}")

    return {**state, "fused_context": "\n".join(context_parts), "sources": list(set(sources))}


async def synthesize_answer(state: GraphRAGState) -> GraphRAGState:
    if not state["fused_context"].strip():
        return {**state, "answer": "I don't have enough information in the knowledge base to answer this question. Please ingest relevant documents first."}

    prompt = f"""You are Paper Brain, an industrial knowledge intelligence assistant for a manufacturing plant.

Answer the following question using ONLY the context provided below.
If the answer is not in the context, say "I don't have enough information in the knowledge base to answer this."
Always cite sources when available. Be concise and direct.

CONTEXT:
{state["fused_context"]}

QUESTION: {state["query"]}

ANSWER:"""

    answer = await chat_complete(prompt)
    return {**state, "answer": answer}


def _route_after_classify(state: GraphRAGState) -> str:
    return state["route"]


def _route_after_qdrant(state: GraphRAGState) -> str:
    return "neo4j" if state["route"] == "hybrid" else "fuse"


def _build_graph():
    graph = StateGraph(GraphRAGState)

    graph.add_node("classify_query", classify_query)
    graph.add_node("retrieve_from_qdrant", retrieve_from_qdrant)
    graph.add_node("retrieve_from_neo4j", retrieve_from_neo4j)
    graph.add_node("fuse_context", fuse_context)
    graph.add_node("synthesize_answer", synthesize_answer)

    graph.set_entry_point("classify_query")

    graph.add_conditional_edges(
        "classify_query",
        _route_after_classify,
        {
            "vector": "retrieve_from_qdrant",
            "graph": "retrieve_from_neo4j",
            "hybrid": "retrieve_from_qdrant"
        }
    )

    graph.add_conditional_edges(
        "retrieve_from_qdrant",
        _route_after_qdrant,
        {
            "neo4j": "retrieve_from_neo4j",
            "fuse": "fuse_context"
        }
    )

    graph.add_edge("retrieve_from_neo4j", "fuse_context")
    graph.add_edge("fuse_context", "synthesize_answer")
    graph.add_edge("synthesize_answer", END)

    return graph.compile()


_graphrag_app = _build_graph()


async def run_query(query: str) -> dict:
    initial_state = GraphRAGState(
        query=query,
        route=None,
        vector_results=[],
        graph_results=[],
        fused_context="",
        answer="",
        sources=[]
    )
    final_state = await _graphrag_app.ainvoke(initial_state)
    return {
        "answer": final_state["answer"],
        "route_taken": final_state["route"],
        "sources": final_state["sources"]
    }
