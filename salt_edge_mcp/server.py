"""
Salt Edge MCP Server — a 7Block Labs build for Salt Edge.

A production-shaped Model Context Protocol server over Salt Edge's API (https://docs.saltedge.com/v6/). Any MCP client
(Claude, ChatGPT, Cursor, agent frameworks) can use Salt Edge's data directly, metered to the caller's
own key — a first-party, agent-native surface instead of community wrappers Salt Edge can't control.

Auth: App-id + Secret headers (Test/Pending apps); Live apps also need Expires-at + Signature. Set SALTEDGE_APP_ID in the environment to call authed endpoints.
Run (stdio):  python -m salt_edge_mcp.server
Run (remote): TRANSPORT=http PORT=8000 python -m salt_edge_mcp.server
"""
from __future__ import annotations
import os
import httpx
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

API = os.environ.get("SALT_EDGE_API_BASE", "https://www.saltedge.com/api/v6")   # override base per deployment if needed
UA = "salt-edge-mcp/1.0 (+https://github.com/7BlockLabs/mcp-salt-edge-demo)"
AUTH_STYLE = "saltedge"   # bearer | header | raw | saltedge | none
AUTH_HEADER = ""
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=True)

mcp = MCPServer("Salt Edge", instructions="Salt Edge data over MCP. Set SALTEDGE_APP_ID for authed calls.")

def _auth_headers() -> dict:
    h = {"User-Agent": UA, "Accept": "application/json"}
    key = os.environ.get("SALTEDGE_APP_ID")
    if AUTH_STYLE == "none":
        return h
    if AUTH_STYLE == "saltedge":              # App-id + Secret headers (Test/Pending apps)
        if os.environ.get("SALTEDGE_APP_ID"): h["App-id"] = os.environ["SALTEDGE_APP_ID"]
        if os.environ.get("SALTEDGE_SECRET"): h["Secret"] = os.environ["SALTEDGE_SECRET"]
        return h
    if key and AUTH_STYLE == "bearer":
        h["Authorization"] = f"Bearer {key}"
    elif key and AUTH_STYLE == "raw":          # raw token in Authorization (e.g. Cube JWT, no 'Bearer')
        h["Authorization"] = key
    elif key and AUTH_STYLE == "header":
        h[AUTH_HEADER] = key
    return h

async def _call(method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=30, headers=_auth_headers()) as c:
        r = await c.request(method, f"{API}{path}", params=params or {}, json=body)
        r.raise_for_status()
        try: return r.json()
        except Exception: return {"raw": r.text[:2000]}

@mcp.tool(title="List Customers", description="List customers created by the application", annotations=READ_ONLY)
async def list_customers(from_id: str | None = None) -> dict:
    return await _call("GET", "/customers", params={"from_id": from_id})

@mcp.tool(title="List Connections", description="List bank connections for a customer", annotations=READ_ONLY)
async def list_connections(customer_id: str | None = None, from_id: str | None = None) -> dict:
    return await _call("GET", "/connections", params={"customer_id": customer_id, "from_id": from_id})

@mcp.tool(title="List Accounts", description="List bank accounts for a connection", annotations=READ_ONLY)
async def list_accounts(connection_id: str | None = None, from_id: str | None = None) -> dict:
    return await _call("GET", "/accounts", params={"connection_id": connection_id, "from_id": from_id})

@mcp.tool(title="List Transactions", description="List posted transactions for a connection/account", annotations=READ_ONLY)
async def list_transactions(connection_id: str | None = None, account_id: str | None = None, from_id: str | None = None) -> dict:
    return await _call("GET", "/transactions", params={"connection_id": connection_id, "account_id": account_id, "from_id": from_id})


def main() -> None:
    if os.environ.get("TRANSPORT") == "http":
        import uvicorn
        uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
    else:
        mcp.run()

if __name__ == "__main__":
    main()
