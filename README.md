# Salt Edge MCP Server

A production-shaped [Model Context Protocol](https://modelcontextprotocol.io) server for **Salt Edge**,
built by **[7Block Labs](https://7blocklabs.com)**. It makes Salt Edge's API usable directly by AI agents
(Claude, ChatGPT, Cursor) — metered to the caller's own key — instead of leaving it to community wrappers.

Built for the Salt Edge team as a working example of the official MCP server we'd ship & launch for you
(OAuth + per-plan metering + listings in the Claude and ChatGPT directories).

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e .
export SALTEDGE_APP_ID=...        # your Salt Edge API key
python -m salt_edge_mcp.server                       # stdio
TRANSPORT=http PORT=8000 python -m salt_edge_mcp.server   # remote
```
Claude Code: `claude mcp add --transport http salt-edge http://localhost:8000/mcp`

API: `https://www.saltedge.com/api/v6` · docs: https://docs.saltedge.com/v6/ · auth: App-id + Secret headers (Test/Pending apps); Live apps also need Expires-at + Signature

## Tools
| Tool | What it does |
|---|---|
| `list_customers` | List customers created by the application |
| `list_connections` | List bank connections for a customer |
| `list_accounts` | List bank accounts for a connection |
| `list_transactions` | List posted transactions for a connection/account |

Want this hardened (OAuth, metering) and listed in Claude + ChatGPT? **[7Block Labs](https://7blocklabs.com)**
builds and launches MCP servers for data & API companies. MIT licensed.
