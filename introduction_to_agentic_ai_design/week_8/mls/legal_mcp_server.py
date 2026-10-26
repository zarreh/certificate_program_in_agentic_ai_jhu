"""
LexAgent MCP tool server.

Runs as a standalone process and exposes five tools over MCP
(streamable HTTP). The notebook connects to it as an MCP client,
so every tool call in the agent is a genuine client -> server round trip.
"""

import os
import json
import re

from mcp.server.fastmcp import FastMCP
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tavily import TavilyClient

# --- Credentials: same config.json the notebook uses ---
with open("../../../config.json", "r") as f:
    config = json.load(f)

os.environ["OPENAI_API_KEY"] = config["API_KEY"]
os.environ["OPENAI_API_BASE"] = config["OPENAI_API_BASE"]

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.0)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
tavily_client = TavilyClient(api_key=config["TAVILY_API_KEY"])

# --- Vector stores: built in-memory from PDFs at server startup ---
def _build_store(pdf_path: str, collection_name: str) -> Chroma:
    docs = PyPDFLoader(pdf_path).load()
    for doc in docs:
        doc.page_content = re.sub(r"\s+", " ", doc.page_content).strip()
    splits = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)
    return Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        collection_name=collection_name,
    )

policy_vectorstore = _build_store("tenants_rights.pdf", "legal_policies")
cases_vectorstore  = _build_store("previous_cases.pdf",  "legal_cases")

# host/port belong in the constructor (server settings), NOT in mcp.run()
mcp = FastMCP("lexagent-tools", host="127.0.0.1", port=8765)


# ---------------------------------------------------------------
# Tool 1: parse_query — deterministic scope check + intent tagging
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

    tenant_keywords = ["tenant", "landlord", "lease", "rent", "eviction", "apartment",
                       "security deposit", "repairs", "housing", "unit", "renter"]
    if not any(k in q for k in tenant_keywords):
        return ("OUT_OF_SCOPE:\n"
                "This agent handles tenant and landlord (housing) law only.\n"
                "Please ask a tenant-related question.")

    if "evict" in q:
        intent = "Eviction Defense / Eviction Process"
    elif "rent increase" in q or "raise rent" in q:
        intent = "Rent Control / Rent Increase Legality"
    elif "security deposit" in q:
        intent = "Security Deposit Dispute"
    elif "repair" in q or "habitability" in q:
        intent = "Repairs & Habitability Rights"
    elif "lease" in q:
        intent = "Lease Review / Interpretation"
    elif "retaliation" in q:
        intent = "Tenant Retaliation Claim"
    elif "discrimination" in q:
        intent = "Housing Discrimination"
    else:
        intent = "General Tenant Rights Inquiry"

    property_type = "Unspecified Residential Unit"
    if "apartment" in q:
        property_type = "Apartment"
    elif "house" in q:
        property_type = "Single-family Home"
    elif "condo" in q:
        property_type = "Condominium"

    tenancy_type = "Unspecified"
    if "month-to-month" in q:
        tenancy_type = "Month-to-Month"
    elif (
        "fixed term" in q or "1 year" in q or "1-year" in q
        or "2-year" in q or "3-year" in q or "4-year" in q or "5-year" in q
        or "two-year" in q or "three-year" in q or "four-year" in q or "five-year" in q
        or "2 year" in q or "3 year" in q or "4 year" in q or "5 year" in q
        or "two year" in q or "three year" in q or "four year" in q or "five year" in q
    ):
        tenancy_type = "Fixed-Term Lease"

    legal_issues = []
    if "notice" in q:
        legal_issues.append("Notice requirements")
    if "deposit" in q:
        legal_issues.append("Security deposit handling")
    if "repair" in q:
        legal_issues.append("Implied warranty of habitability")
    if "lockout" in q or "change the locks" in q or "changing locks" in q:
        legal_issues.append("Illegal lockout / self-help eviction")
    if "sublet" in q or "subletting" in q or "airbnb" in q:
        legal_issues.append("Unauthorized subletting")
    if "rent" in q:
        legal_issues.append("Rent payment obligations")
    if not legal_issues:
        legal_issues.append("General tenant protections")

    return f"""Parsed Tenant Law Query
-----------------------
Scope Validation: Tenant / Landlord Law CONFIRMED
User Intent: {intent}
Jurisdiction: New York, US (fixed for this demo)
Property Type: {property_type}
Tenancy Type: {tenancy_type}
Key Legal Issues:
- """ + "\n- ".join(legal_issues)


# ---------------------------------------------------------------
# Tool 2: policy_search_tool — RAG over the policy knowledge base
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
    docs = policy_vectorstore.similarity_search(query, k=2)
    if not docs:
        return "No relevant legal policy found in the knowledge base."

    return "\n\n".join(
        f"Policy Excerpt {i}:\n{doc.page_content}" for i, doc in enumerate(docs, 1)
    )


# ---------------------------------------------------------------
# Tool 3: cases_search_tool — RAG over prior case documents
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
    docs = cases_vectorstore.similarity_search(query, k=3)
    if not docs:
        return "No relevant legal cases found in the knowledge base."

    return "\n\n".join(
        f"Case Precedent {i}:\n{doc.page_content}" for i, doc in enumerate(docs, 1)
    )


# ---------------------------------------------------------------
# Tool 4: tavily_web_search_tool — live web search for recent cases
# ---------------------------------------------------------------
@mcp.tool()
def tavily_web_search_tool(query: str) -> str:
    """
    Search the live web for recent New York rent-related legal
    developments — newly enacted statutes, court rulings from 2023
    onwards, and current regulatory changes — that are not yet in
    the local knowledge base. Use this tool when local retrieval
    (policy_search_tool or cases_search_tool) returns no result
    that directly addresses the user's question about current or
    recent law.
    """
    response = tavily_client.search(query=query, max_results=5, search_depth="advanced")
    results = response.get("results", [])
    if not results:
        return "No recent New York rent-related legal results found."

    return "\n\n".join(
        f"Result {i}:\n{r.get('content', 'No content')}\nSource: {r.get('url', 'n/a')}"
        for i, r in enumerate(results, 1)
    )


# ---------------------------------------------------------------
# Tool 5: rewrite_legal_clause — LLM rewrite grounded in evidence
# ---------------------------------------------------------------
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
    prompt = f"""You are a legal drafting assistant.

Rewrite the ORIGINAL CLAUSE so that it fully complies with the applicable
law described in the POLICY EXCERPTS and CASE LAW below, while remaining
as landlord-protective as legally permitted. Base every change ONLY on
the provided materials — do not invent statutes or citations.

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
    response = llm.invoke(prompt)
    return response.content


# ---------------------------------------------------------------
# Run server over streamable HTTP (endpoint: http://127.0.0.1:8765/mcp)
# ---------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
