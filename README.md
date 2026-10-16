# Python AI Agent V2 — Multi-Tool Agent

A beginner-friendly, runnable AI agent built with Python and the OpenAI Responses API. The agent decides when to call tools, receives their outputs, and continues until it can answer your question.

## Features

- **Web search:** Uses OpenAI's built-in web search tool through a separate API request.
- **Calculator:** Evaluates basic arithmetic safely without Python `eval()`.
- **SQLite:** Queries a local, automatically created sample sales database (read-only).
- **Clock:** Returns the current time in UTC.
- **Agent loop:** Processes function calls and feeds tool outputs back to the model, up to eight rounds.
- **Visibility:** Prints tool calls to the terminal so you can observe the agent's decisions.

## Requirements

- Python 3.10 or later (3.11+ recommended)
- An OpenAI API key with available API credits
- Internet access for API requests and web searches

**Important:** OpenAI API usage is billed separately from ChatGPT subscriptions. Web search and multiple tool steps may increase costs. Check the current API pricing and model/tool availability in your account.

## Quick start (Windows PowerShell)

1. Extract the ZIP file and open `python_ai_agent_v2` in VS Code.
2. Open a terminal in that folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt with `.venv\Scripts\activate.bat` instead.

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

6. Open `.env` and replace `replace_with_your_key` with your real API key. Never commit or share this file.
7. Run the agent:

   ```powershell
   python agent.py "What is 125 * 18 + 40?"
   ```

## Quick start (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
python agent.py "What is 125 * 18 + 40?"
```

## Try these examples

### Calculator

```bash
python agent.py "Calculate (125 * 18 + 40) / 5"
```

### SQL analysis

```bash
python agent.py "Using the sample sales database, calculate revenue by product and identify the highest revenue product."
```

The database is created automatically as `sales.db` on first run. It contains a `sales` table:

| Column | Type | Meaning |
|---|---|---|
| id | INTEGER | Sale ID |
| product | TEXT | Product name |
| quantity | INTEGER | Units sold |
| unit_price | REAL | Price per unit |

Revenue is `quantity * unit_price`. This is demo data, not live sales.

### Web search

```bash
python agent.py "Find recent developments in Python AI agents and provide source links."
```

### Multiple tools

```bash
python agent.py "What is the current UTC time? Then calculate the total revenue in the sample database."
```

### Hide tool logs

```bash
python agent.py --quiet "What is 10% of 450?"
```

## How the agent works

```text
User question
     |
     v
OpenAI model (decides next action)
     |
     +---- calculator(expression)
     +---- query_sql(sql)
     +---- current_utc_time()
     +---- web_search(query)
     |
     v
Python executes the requested tool
     |
     v
Tool result goes back to the model
     |
     +---- repeat if more tools are needed (max 8 rounds)
     |
     v
Final answer
```

The `agent.py` file defines function-tool schemas and the loop. The `tools.py` file contains local tool implementations. `web_search` makes an additional OpenAI Responses API request using the hosted `web_search` tool.

## Project structure

```text
python_ai_agent_v2/
├── agent.py            # OpenAI function calling and agent loop
├── tools.py            # Calculator, SQLite, clock
├── requirements.txt    # Python packages
├── .env.example        # API configuration template
├── .gitignore          # Files excluded from version control
├── tests/
│   └── test_tools.py   # Offline unit tests
└── README.md
```

## Run tests (no API key required)

```bash
python -m unittest discover -s tests -v
```

## Security notes

- The calculator parses arithmetic with Python's AST; it does not execute arbitrary Python code.
- SQLite is opened read-only, and an SQLite authorizer rejects write operations.
- This project uses only a local sample database. Do not point it at production databases without adding authentication, permissions, query validation, auditing, and stronger resource limits.
- Web search results and tool outputs are untrusted; the system instructions tell the model not to follow instructions found in those results.
- Tool calls are capped at eight rounds, and SQL output is limited to 100 rows.
- The demo is **not** a hardened production service.

## Troubleshooting

**`OPENAI_API_KEY is missing`**: Create `.env` next to `agent.py`, then set a valid key.

**`ModuleNotFoundError`**: Activate your virtual environment and reinstall `requirements.txt`.

**`401 Unauthorized`**: Check your API key and account access.

**`429` / quota errors**: Review API billing, rate limits, and credits.

**Model or web search unavailable**: Check supported models and tools in your OpenAI API account. You can change `OPENAI_MODEL` in `.env` to a model that supports function calling and web search.

**Database has unexpected data**: Delete `sales.db` and rerun the program to recreate the demo dataset.

## Next steps

- Add an interactive chat interface with Streamlit.
- Add human approval before high-impact actions.
- Add structured JSON output and report export.
- Add persistent conversation memory.
- Connect to a staging API or a strictly read-only analytics database.

## Verification status

Local Python syntax checks and offline tool unit tests can run without an API key. A live end-to-end run requires your own OpenAI API key and billing access.
