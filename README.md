# Google Calendar MCP Server

A local [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that exposes Google Calendar as a tool for Claude Desktop — ask Claude natural-language questions about your schedule, and it fetches real data from your actual Google Calendar.

## What it does

- Connects to Claude Desktop as an MCP server over stdio
- Authenticates with Google Calendar via OAuth 2.0 (Desktop app flow)
- Exposes a `list_events` tool that returns upcoming events from the user's primary calendar

Example: ask Claude Desktop *"What's on my calendar?"* and it calls this server behind the scenes to fetch and summarize your actual events.

## Tech stack

- **Python 3.12**
- **MCP Python SDK** (`mcp`) — server framework, tool registration via `@mcp.tool()`
- **Google Calendar API** (`google-api-python-client`) — fetching calendar data
- **OAuth 2.0** (`google-auth-oauthlib`) — Desktop app authentication flow
- **Transport**: stdio (Claude Desktop launches the server as a subprocess and communicates over stdin/stdout)

## Architecture

Claude Desktop acts as the MCP client. When it starts, it launches this server as a subprocess and discovers its available tools. When a user asks a calendar-related question:

1. Claude (the model) decides to call `list_events`, based on the tool's description and schema
2. Claude Desktop sends that call to this server over stdio, using MCP's JSON-RPC protocol
3. The server authenticates with Google (using a saved OAuth token, refreshing silently if needed) and calls the real Google Calendar REST API
4. The server returns the results, which flow back through Claude Desktop to the model, which replies in natural language

Three distinct message formats are involved end-to-end: the Anthropic API format (Claude Desktop ↔ the model), MCP's JSON-RPC format (Claude Desktop ↔ this server), and Google's own REST API format (this server ↔ Google Calendar).

## Setup

1. **Clone the repo**
   ```
   git clone https://github.com/aukay13/google-calendar-mcp-server.git
   cd google-calendar-mcp-server
   ```

2. **Create a virtual environment**
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Get your own Google Calendar API credentials**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com)
   - Enable the Google Calendar API
   - Configure the OAuth consent screen (External, add yourself as a test user)
   - Create OAuth credentials (type: Desktop app)
   - Download the credentials file, save it in the project root as `credentials.json`

   > `credentials.json` and `token.json` are gitignored — you must supply your own; they're never included in this repo.

5. **Add the server to Claude Desktop's config** (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "calendar-server": {
         "command": "<path-to-venv>\\Scripts\\python.exe",
         "args": ["<path-to-project>\\calendar_server.py"]
       }
     }
   }
   ```
   Restart Claude Desktop fully (not just close the window) after editing.

6. On first use, a browser window will open asking you to log in and grant calendar access. After that, a `token.json` is saved locally and no further login is needed.

## Current capability

- `list_events(max_results: int = 10)` — read-only access, lists upcoming events with start time and title

## Planned expansion

This project is intentionally scoped small to focus on learning core MCP concepts first. Natural next step: a **`create_event` tool**, allowing Claude to add new events directly to the calendar — this would require:
- Upgrading the OAuth scope from read-only to write access (`calendar.events` or `calendar`)
- Re-authenticating (deleting the existing `token.json` to trigger fresh consent under the new scope)
- A new `@mcp.tool()`-decorated function accepting event details (title, start/end time) and calling Google's `events().insert()` API

Other possible extensions: date-range filtering (currently only supports a result count, not an actual date range), and a `streamable-http` transport variant for running the server independently of Claude Desktop's process lifecycle.

## Disclaimer

Built as a hands-on learning project to understand MCP (Model Context Protocol) concepts — tool registration, discovery, transports, and the client-server protocol — using a real, practical integration rather than a toy example.