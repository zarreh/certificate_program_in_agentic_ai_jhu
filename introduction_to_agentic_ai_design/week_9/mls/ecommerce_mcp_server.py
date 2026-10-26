# Write the MCP server to disk. It exposes the e-commerce data layer as MCP tools.
# Design decision — LEAST PRIVILEGE: lookup_customer returns ONLY task-necessary fields
# (loyalty tier, account status, city). It never returns email, phone, full address, DOB, or SSN.
# The best redactor is the query that never fetched the sensitive data in the first place.
import json, os
from mcp.server.fastmcp import FastMCP

# host/port belong in the constructor (server settings), NOT in mcp.run()
mcp = FastMCP("ecommerce-tools", host="127.0.0.1", port=8765)

DATA_DIR = os.environ.get("MCP_DATA_DIR", "data")
def _load(name):
    with open(os.path.join(DATA_DIR, f"{name}.json")) as f:
        return json.load(f)


@mcp.tool()
def lookup_customer(customer_id: str) -> str:
    """Look up minimal, non-sensitive customer profile fields by customer ID (e.g. CUST-2001)."""
    c = next((x for x in _load("customers") if x["customer_id"] == customer_id), None)
    if not c:
        return f"No customer found with ID {customer_id}."
    # LEAST PRIVILEGE: deliberately omit email, phone, address, DOB, ssn_last_four.
    return json.dumps({
        "customer_id": c["customer_id"],
        "account_status": c.get("account_status"),
        "loyalty_tier": c.get("loyalty_tier"),
        "city": c.get("home_address", {}).get("city"),
    })

@mcp.tool()
def track_order(order_id: str) -> str:
    """Return status, dates, carrier, and free-text notes for an order (e.g. ORD-10001)."""
    o = next((x for x in _load("orders") if x["order_id"] == order_id), None)
    if not o:
        return f"No order found with ID {order_id}."
    return json.dumps({
        "order_id": o["order_id"], "status": o.get("status"),
        "order_date": o.get("order_date"), "estimated_delivery": o.get("estimated_delivery"),
        "carrier": o.get("carrier"), "tracking_number": o.get("tracking_number"),
        "notes": o.get("notes", ""),   # NOTE: free-text notes are UNTRUSTED — see Section 3 (tool poisoning)
    })

@mcp.tool()
def search_products(query: str) -> str:
    """Search the product catalog by a keyword in the product name."""
    q = query.lower()
    hits = [{"product_id": p["product_id"], "name": p["name"], "price": p["price"],
             "in_stock": p.get("stock_quantity", 0) > 0}
            for p in _load("products") if q in p["name"].lower()]
    return json.dumps(hits) if hits else f"No products matching '{query}'."

@mcp.tool()
def get_payment_summary(order_id: str) -> str:
    """Return a privacy-safe payment summary: method and masked card last-4 only."""
    p = next((x for x in _load("payments") if x["order_id"] == order_id), None)
    if not p:
        return f"No payment found for order {order_id}."
    cd = p.get("card_details", {}) or {}
    return json.dumps({
        "order_id": p["order_id"], "method": p.get("payment_method"),
        "amount": p.get("amount"), "status": p.get("status"),
        "card_last_four": cd.get("card_last_four"),   # full number/CVV are NOT in the dataset — cannot leak
    })

@mcp.tool()
def get_return_claim(claim_id: str) -> str:
    """Fetch a return claim by ID (e.g. RET-5001)."""
    r = next((x for x in _load("returns") if x["claim_id"] == claim_id), None)
    return json.dumps(r) if r else f"No return claim found with ID {claim_id}."

@mcp.tool()
def initiate_refund(claim_id: str, amount: float) -> str:
    """Issue a refund for a claim. SERVER-SIDE symbolic rule: refunds above the policy limit
    are physically refused here, regardless of what the agent decides."""
    # Threshold flows from GUARDRAIL_CONFIG via the REFUND_AUTO_LIMIT env var (set in the launch cell).
    LIMIT = float(os.environ.get("REFUND_AUTO_LIMIT", "50.00"))
    if amount > LIMIT:
        return json.dumps({"ok": False,
            "reason": f"REFUSED: amount ${amount:.2f} exceeds auto-approve limit ${LIMIT:.2f}. Route to manual review."})
    return json.dumps({"ok": True, "refund_id": f"RFND-{claim_id[-4:]}", "amount": amount})
# ---------------------------------------------------------------
# Run server over streamable HTTP (endpoint: http://127.0.0.1:8765/mcp)
# ---------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
