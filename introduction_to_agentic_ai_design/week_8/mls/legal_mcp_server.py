"""
LexAgent MCP tool server.

Runs as a standalone process and exposes five tools over MCP (streamable HTTP),
so every tool call made by the agent is a genuine client -> server round trip.
"""

import json
import os
import re

from mcp.server.fastmcp import FastMCP
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tavily import TavilyClient

# Same config.json as the notebook
with open("../../../config.json") as f:
    config = json.load(f)
os.environ["OPENAI_API_KEY"] = config["API_KEY"]
os.environ["OPENAI_API_BASE"] = config["OPENAI_API_BASE"]
os.environ["TAVILY_API_KEY"] = config["TAVILY_API_KEY"]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
tavily = TavilyClient()


# --- RAG knowledge bases: PDF -> chunks -> in-memory Chroma -> retriever -----
def build_retriever(pdf_path: str, collection: str, k: int):
    docs = PyPDFLoader(pdf_path).load()
    for d in docs:  # pypdf emits stray newlines; collapse them for cleaner chunks
        d.page_content = re.sub(r"\s+", " ", d.page_content).strip()
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    store = Chroma.from_documents(chunks, embeddings, collection_name=collection)
    return store.as_retriever(search_kwargs={"k": k})


policy_retriever = build_retriever("tenants_rights.pdf", "legal_policies", k=2)
cases_retriever = build_retriever("previous_cases.pdf", "legal_cases", k=3)


def format_hits(docs, label: str, empty_message: str) -> str:
    hits = [f"{label} {i}:\n{d.page_content}" for i, d in enumerate(docs, 1)]
    return "\n\n".join(hits) or empty_message


# host/port belong in the constructor (server settings), NOT in mcp.run()
mcp = FastMCP("lexagent-tools", host="127.0.0.1", port=8765)

# --- Rule tables for parse_query (deterministic, cheap, easy to audit) --------
SCOPE = r"\b(tenants?|landlords?|lease|rent\w*|evict\w*|apartment|security deposit|repairs?|housing|units?|renters?)\b"
INTENTS = [
    (r"evict", "Eviction Defense / Eviction Process"),
    (r"rent increase|raise rent", "Rent Control / Rent Increase Legality"),
    (r"security deposit", "Security Deposit Dispute"),
    (r"repair|habitability", "Repairs & Habitability Rights"),
    (r"lease", "Lease Review / Interpretation"),
    (r"retaliation", "Tenant Retaliation Claim"),
    (r"discrimination", "Housing Discrimination"),
]
PROPERTY_TYPES = [(r"apartment", "Apartment"), (r"house", "Single-family Home"), (r"condo", "Condominium")]
ISSUES = [
    (r"notice", "Notice requirements"),
    (r"deposit", "Security deposit handling"),
    (r"repair", "Implied warranty of habitability"),
    (r"lockout|change the locks|changing locks", "Illegal lockout / self-help eviction"),
    (r"sublet|airbnb", "Unauthorized subletting"),
    (r"rent", "Rent payment obligations"),
]


def first_match(table, q: str, default: str) -> str:
    return next((label for pattern, label in table if re.search(pattern, q)), default)


# ---------------------------------------------------------------
# Tool 1: parse_query -- scope check + intent tagging
# ---------------------------------------------------------------
@mcp.tool()
def parse_query(query: str) -> str:
    """
    Validate that a query is about tenant/landlord (housing) law and tag
    its intent, property type, tenancy type, and key legal issues.
    Rejects out-of-scope queries. Rule-based by design: deterministic,
    cheap, and easy to audit. Jurisdiction is fixed to New York for this
    demo implementation.
    """
    q = query.lower()
    if not re.search(SCOPE, q):
        return (
            "OUT_OF_SCOPE:\n"
            "This agent handles tenant and landlord (housing) law only.\n"
            "Please ask a tenant-related question."
        )

    if "month-to-month" in q:
        tenancy = "Month-to-Month"
    elif re.search(r"fixed[- ]term|\b(1|2|3|4|5|one|two|three|four|five)[- ]year", q):
        tenancy = "Fixed-Term Lease"
    else:
        tenancy = "Unspecified"
    issues = [label for pattern, label in ISSUES if re.search(pattern, q)] or ["General tenant protections"]

    return (
        "Parsed Tenant Law Query\n"
        "-----------------------\n"
        "Scope Validation: Tenant / Landlord Law CONFIRMED\n"
        f"User Intent: {first_match(INTENTS, q, 'General Tenant Rights Inquiry')}\n"
        "Jurisdiction: New York, US (fixed for this demo)\n"
        f"Property Type: {first_match(PROPERTY_TYPES, q, 'Unspecified Residential Unit')}\n"
        f"Tenancy Type: {tenancy}\n"
        "Key Legal Issues:\n- " + "\n- ".join(issues)
    )


# ---------------------------------------------------------------
# Tool 2: policy_search_tool -- RAG over the policy knowledge base
# ---------------------------------------------------------------
@mcp.tool()
def policy_search_tool(query: str) -> str:
    """
    Semantic search over the local tenant-rights policy knowledge base,
    which covers foundational New York housing statutes, established
    regulations, and tenant protections compiled before 2023. Returns
    the top relevant policy excerpts. For recently enacted laws or
    regulatory changes from 2023 onwards, supplement with
    tavily_web_search_tool if this tool returns no directly relevant result.
    """
    return format_hits(
        policy_retriever.invoke(query), "Policy Excerpt",
        "No relevant legal policy found in the knowledge base.",
    )


# ---------------------------------------------------------------
# Tool 3: cases_search_tool -- RAG over prior case documents
# ---------------------------------------------------------------
@mcp.tool()
def cases_search_tool(query: str) -> str:
    """
    Semantic search over a curated collection of prior New York
    housing-court case documents (cases decided before 2023).
    Returns the top relevant case precedents. For court decisions
    from 2023 onwards or recently argued cases, supplement with
    tavily_web_search_tool if this tool returns no relevant result.
    """
    return format_hits(
        cases_retriever.invoke(query), "Case Precedent",
        "No relevant legal cases found in the knowledge base.",
    )


# ---------------------------------------------------------------
# Tool 4: tavily_web_search_tool -- live web search for recent law
# ---------------------------------------------------------------
@mcp.tool()
def tavily_web_search_tool(query: str) -> str:
    """
    Search the live web for recent New York rent-related legal
    developments -- newly enacted statutes, court rulings from 2023
    onwards, and current regulatory changes -- that are not yet in
    the local knowledge base. Use this tool when local retrieval
    (policy_search_tool or cases_search_tool) returns no result
    that directly addresses the user's question about current or
    recent law.
    """
    results = tavily.search(query=query, max_results=5, search_depth="advanced")["results"]
    hits = [f"Result {i}:\n{r['content']}\nSource: {r['url']}" for i, r in enumerate(results, 1)]
    return "\n\n".join(hits) or "No recent New York rent-related legal results found."


# ---------------------------------------------------------------
# Tool 5: rewrite_legal_clause -- LLM rewrite grounded in evidence
# ---------------------------------------------------------------
rewrite_chain = (
    ChatPromptTemplate.from_template(
        """You are a legal drafting assistant.

Rewrite the ORIGINAL CLAUSE so that it fully complies with the applicable
law described in the POLICY EXCERPTS and CASE LAW below, while remaining
as landlord-protective as legally permitted. Base every change ONLY on
the provided materials -- do not invent statutes or citations.

PARSED CLAIM CONTEXT:
{parsed_claim}

POLICY EXCERPTS:
{policy_excerpts}

CASE LAW EXCERPTS:
{case_law_excerpts}

ORIGINAL CLAUSE:
{original_clause}

Return: (1) the rewritten clause(s), then (2) a brief bullet list of what
was changed and why."""
    )
    | llm
    | StrOutputParser()
)


@mcp.tool()
def rewrite_legal_clause(
    original_clause: str,
    parsed_claim: str,
    policy_excerpts: str,
    case_law_excerpts: str,
) -> str:
    """
    Rewrite a lease clause (or set of clauses) for legal compliance,
    grounded in previously retrieved evidence. Call this AFTER
    parse_query, policy_search_tool, and cases_search_tool so their
    outputs can be passed in as arguments.
    """
    return rewrite_chain.invoke(
        {
            "original_clause": original_clause,
            "parsed_claim": parsed_claim,
            "policy_excerpts": policy_excerpts,
            "case_law_excerpts": case_law_excerpts,
        }
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # endpoint: http://127.0.0.1:8765/mcp
