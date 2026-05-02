# Graph MVP: Codebase Sketch

This is what the first 2-3 weeks of building looks like. The goal is a working demo that takes synthetic HVAC distributor data, compiles it into a living wiki, and answers natural-language questions against it with full audit traces. Obsidian is the viewer. Claude is the model. Everything runs on a laptop.

---

## Tech Stack

**Language:** Python 3.11+. It's the right choice for LLM orchestration work — every library you need is Python-first, and the ecosystem for agent frameworks, data ingestion, and LLM APIs is significantly ahead of anything else. If you prefer TypeScript for the web UI, that's fine, but keep the core pipeline in Python.

**LLM API:** Anthropic (Claude) to start. The `anthropic` Python SDK is clean, tool use works well, and Claude is genuinely the best at the kind of multi-step agent navigation your product needs. Single provider means simpler code for the MVP. Add routing to Together AI or Fireworks later when costs start mattering — around customer 3-5.

**Agent framework:** Don't use one. Seriously. LangChain, LlamaIndex, CrewAI, and the rest add complexity and abstraction that fights you when you need to debug what the agent is actually doing. For an MVP, write a simple agent loop by hand — it's maybe 200 lines of code and you'll understand every piece of it. You can adopt a framework later if you hit a wall, but most successful LLM products end up writing their own agent loops anyway.

**Structured storage:** DuckDB. It's a single-file embedded database that's shockingly good at analytical queries over millions of rows, runs on a laptop with zero setup, and has a clean Python API. This is where the high-volume tabular data lives (orders, inventory, transactions).

**Wiki storage:** Just markdown files in a folder. No database, no fancy indexing. The LLM reads and writes them directly. Use a simple naming convention (`skus/CAP-TURBO-200.md`, `suppliers/global-hvac.md`, `customers/acme-heating.md`) and let backlinks happen via markdown links.

**Wiki viewer:** Obsidian. Free, beautiful, renders markdown with backlinks automatically, has a graph view that looks amazing in demos. Point it at your wiki folder and you get a polished UI for free. This is a huge win for the demo — you don't have to build a wiki viewer.

**Web chat UI:** FastAPI backend + a minimal React or plain HTML/JS frontend. Nothing fancy — an input box, a message history, and a "show sources" expandable panel for audit traces. 300-500 lines of code total.

**Audit logging:** SQLite. One table, one row per agent action, with the full trace as JSON. Simple, queryable, and easy to demo ("click this button to see exactly what the agent did").

**Data ingest:** Start with CSV files because that's the lowest common denominator for ERP exports. Every HVAC distributor's ERP (DDI System, Epicor Eclipse, Infor SX.e) can export CSVs, and a lot of the data you need is already available that way. Add PDF parsing (for supplier sheets) via `pdfplumber` or `unstructured`. Add email parsing later if needed. Don't build database connectors for the MVP — they're too customer-specific and add weeks of work for no demo value.

**Synthetic data:** Write a Python script that generates realistic HVAC distributor data — 5k SKUs, 20 suppliers, 500 customers, 2 years of orders. Use real HVAC parts categories and manufacturer names (publicly available from HARDI, Grainger catalogs, etc.) so the demo feels authentic.

---

## Directory Structure

```
graph-mvp/
├── README.md
├── pyproject.toml              # or requirements.txt
├── .env.example                # ANTHROPIC_API_KEY, etc.
│
├── src/
│   ├── __init__.py
│   │
│   ├── ingest/                 # Raw data → structured staging
│   │   ├── __init__.py
│   │   ├── csv_loader.py       # Load ERP CSV exports into DuckDB
│   │   ├── pdf_parser.py       # Extract text from supplier PDFs
│   │   └── synthetic.py        # Generate fake HVAC distributor data
│   │
│   ├── compile/                # Staging → wiki
│   │   ├── __init__.py
│   │   ├── compiler.py         # Main LLM wiki compilation loop
│   │   ├── sku_pages.py        # Generate SKU markdown pages
│   │   ├── supplier_pages.py   # Generate supplier markdown pages
│   │   ├── customer_pages.py   # Generate customer markdown pages
│   │   ├── index_pages.py      # Generate category and overview indexes
│   │   └── templates/          # Markdown templates for page types
│   │       ├── sku.md.j2
│   │       ├── supplier.md.j2
│   │       └── customer.md.j2
│   │
│   ├── agent/                  # The query and maintenance agents
│   │   ├── __init__.py
│   │   ├── loop.py             # Core agent loop (the 200 lines)
│   │   ├── tools.py            # Agent tool definitions
│   │   ├── router.py           # Model routing (all Claude for MVP)
│   │   └── prompts.py          # System prompts for different agent modes
│   │
│   ├── tools/                  # Functions the agent can call
│   │   ├── __init__.py
│   │   ├── wiki_read.py        # read_wiki_page, search_wiki, follow_link
│   │   ├── sql_query.py        # run_sql against DuckDB
│   │   └── web_search.py       # Optional: for health checks and imputation
│   │
│   ├── audit/                  # Trace logging
│   │   ├── __init__.py
│   │   ├── logger.py           # Append-only trace logger
│   │   └── schema.sql          # SQLite audit table schema
│   │
│   ├── api/                    # FastAPI backend for the chat UI
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app
│   │   ├── chat.py             # POST /chat endpoint
│   │   └── audit.py            # GET /audit/{trace_id} endpoint
│   │
│   └── config.py               # Paths, model names, etc.
│
├── data/
│   ├── raw/                    # Input CSVs, PDFs, etc.
│   ├── staging.duckdb          # DuckDB file with mirrored ERP tables
│   ├── wiki/                   # The markdown wiki (Obsidian vault)
│   │   ├── _index.md           # Top-level entry point
│   │   ├── skus/
│   │   ├── suppliers/
│   │   ├── customers/
│   │   ├── warehouses/
│   │   ├── refrigerants/
│   │   └── concepts/           # Cross-cutting concepts like "R-410A phase-out"
│   └── audit.sqlite            # Audit trace log
│
├── web/                        # Minimal chat UI
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── scripts/
│   ├── generate_synthetic_data.py    # Create fake HVAC distributor data
│   ├── run_full_pipeline.py          # Ingest → compile → ready to query
│   └── demo_queries.py               # Canned questions for the demo
│
└── tests/
    └── ...
```

---

## The Core Agent Loop (The 200 Lines)

This is the heart of the system. It's simpler than you'd expect. Pseudocode:

```python
# src/agent/loop.py

def run_agent(user_question: str, trace_id: str) -> AgentResponse:
    conversation = [
        {"role": "user", "content": user_question}
    ]
    
    max_iterations = 15
    for iteration in range(max_iterations):
        # Call Claude with the current conversation and available tools
        response = claude_api.messages.create(
            model="claude-opus-4-6",
            system=AGENT_SYSTEM_PROMPT,
            messages=conversation,
            tools=AGENT_TOOLS,
            max_tokens=4096,
        )
        
        # Log the agent's action to the audit trail
        audit_logger.log(trace_id, iteration, response)
        
        # If Claude wants to use a tool, execute it and loop
        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    audit_logger.log_tool_result(trace_id, block.name, result)
                    conversation.append({"role": "assistant", "content": response.content})
                    conversation.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        }]
                    })
        
        # If Claude is done, return the final answer
        elif response.stop_reason == "end_turn":
            final_answer = extract_text(response)
            return AgentResponse(
                answer=final_answer,
                trace_id=trace_id,
                iterations=iteration + 1
            )
    
    # Hit max iterations without a final answer
    return AgentResponse(
        answer="I wasn't able to complete the research for this question in the allowed number of steps.",
        trace_id=trace_id,
        iterations=max_iterations
    )
```

The agent's tools are the toolkit it uses to navigate the wiki and query DuckDB:

```python
# src/agent/tools.py

AGENT_TOOLS = [
    {
        "name": "read_wiki_page",
        "description": "Read the full contents of a wiki page by its path",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "e.g. 'skus/CAP-TURBO-200.md'"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "search_wiki",
        "description": "Full-text search across all wiki pages. Returns matching pages with snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_wiki_directory",
        "description": "List all files in a wiki subdirectory",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "e.g. 'skus' or 'suppliers'"}
            },
            "required": ["directory"]
        }
    },
    {
        "name": "run_sql",
        "description": "Run a SQL query against the DuckDB staging database. Available tables: orders, inventory, customers, skus, suppliers, warehouses.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A valid SQL query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_schema",
        "description": "Get the schema (columns and types) for a DuckDB table",
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {"type": "string"}
            },
            "required": ["table"]
        }
    }
]
```

The system prompt tells Claude how to approach questions. Roughly:

```
You are an operations intelligence agent for an HVAC parts distributor. 
You have access to two sources of truth about the business:

1. A wiki of markdown files containing knowledge about products, suppliers,
   customers, refrigerants, and operational concepts. Use read_wiki_page,
   search_wiki, and list_wiki_directory to navigate it.

2. A DuckDB database containing the tabular operational data: orders,
   inventory, customers, skus, suppliers, warehouses. Use run_sql for
   precise numeric queries, aggregations, and anything involving counts,
   sums, or historical data.

For any question, think about whether you need knowledge (use the wiki),
facts (use SQL), or both (use both). Cite your sources in your final 
answer — both the wiki pages you read and the SQL queries you ran.

Work step by step. Don't guess — if you're not sure, read more wiki pages
or run more queries. When you have enough information, give a clear,
concise answer with citations.
```

That's basically the whole agent. The rest is just the pipeline that builds the wiki in the first place and the UI that exposes it to users.

---

## The Compilation Pipeline

This is the other half of the system — the part that takes raw data and produces the wiki. Also simpler than you'd expect.

```python
# src/compile/compiler.py

def compile_wiki(duckdb_conn, wiki_dir, raw_dir):
    """
    Compile raw data into a structured markdown wiki.
    Runs once on initial deploy, then incrementally when new data arrives.
    """
    
    # Step 1: Generate SKU pages from the skus table
    skus = duckdb_conn.execute("SELECT * FROM skus").fetchall()
    for sku in tqdm(skus, desc="Generating SKU pages"):
        # For each SKU, ask Claude to write a markdown page that:
        # - Describes the SKU based on its ERP fields
        # - Links to its supplier, manufacturer, warehouse
        # - Identifies substitutes (using LLM reasoning over similar SKUs)
        # - Notes any refrigerant or regulatory concerns
        # - Embeds a metadata block referencing the orders table for history
        page_content = generate_sku_page(sku, duckdb_conn)
        write_wiki_file(wiki_dir / f"skus/{sku.id}.md", page_content)
    
    # Step 2: Generate supplier pages
    suppliers = duckdb_conn.execute("SELECT * FROM suppliers").fetchall()
    for supplier in tqdm(suppliers, desc="Generating supplier pages"):
        page_content = generate_supplier_page(supplier, duckdb_conn)
        write_wiki_file(wiki_dir / f"suppliers/{supplier.id}.md", page_content)
    
    # Step 3: Generate customer pages, warehouse pages, etc.
    # ...
    
    # Step 4: Generate concept pages
    # These are the cross-cutting ones like "R-410A phase-out exposure",
    # "Lennox tariff impact", "top 10 customers by revenue"
    # Claude generates these by reading other wiki pages and synthesizing
    generate_concept_pages(wiki_dir, duckdb_conn)
    
    # Step 5: Generate indexes
    # Category indexes, overall _index.md, cross-reference tables
    generate_indexes(wiki_dir)
    
    # Step 6: Health check
    # Claude reads a sample of the wiki and flags inconsistencies
    run_health_check(wiki_dir, duckdb_conn)
```

Each `generate_*_page` function is a Claude call with a prompt that says "here's the structured data for this SKU, here's the template, write a markdown page that follows the template and includes backlinks to related entities." The LLM does the work of turning flat data into linked narrative.

This is the Karpathy pattern, applied to HVAC distributor data instead of research papers.

---

## What the Demo Looks Like

After running the pipeline on synthetic data, you have:

1. **A DuckDB file** with realistic HVAC distributor tables (5k SKUs, 20 suppliers, 500 customers, 2 years of orders).

2. **A wiki folder** with ~6k markdown pages, fully linked, that you can open in Obsidian and browse. The Obsidian graph view is visually impressive — it shows thousands of nodes and edges, the actual knowledge structure of the business.

3. **A web chat UI** where you can ask questions like:
   - "What's our exposure to the R-410A phase-out?"
   - "Which customers are most affected by the recent Lennox tariff increase?"
   - "Show me suppliers we depend on for more than 20% of a single category"
   - "What are good substitute parts for CAP-TURBO-200?"
   
   Each answer shows up in chat with a "show sources" button. Clicking it reveals the full audit trace — which wiki pages the agent read, which SQL queries it ran, and the intermediate reasoning.

4. **The demo video** is 2 minutes: ask a question, show the answer, click "show sources" to demonstrate auditability, open Obsidian to show the living wiki with its graph view, explain that this entire system was built from the distributor's raw data in 4 weeks.

That demo is what you take to HARDI and to PE operating partners. It's what goes in the YC application. It's what closes the first customer.

---

## Week-by-Week Build Plan

**Week 1:**
- Set up project, install dependencies, get Claude API working
- Build synthetic data generator
- Build DuckDB ingest from CSVs
- Verify you can query the DuckDB from Python

**Week 2:**
- Build the wiki compilation pipeline
- Generate SKU, supplier, customer, and warehouse pages
- Generate basic concept pages (refrigerants, tariff exposure)
- Open result in Obsidian, verify backlinks and graph view work

**Week 3:**
- Build the agent loop with tool use
- Build audit logging
- Build FastAPI chat backend
- Build minimal web UI
- Run end-to-end demo queries and iterate on prompts until answers are solid

**Week 4 (buffer):**
- Polish the demo
- Record the 2-minute demo video
- Prepare the 48-hour pilot pitch for HARDI and PE outreach

---

## What's Deliberately NOT in the MVP

- **Real ERP connectors.** CSV ingest only. Database connectors are customer-specific and add weeks of work for zero demo value.
- **Multi-tenant infrastructure.** Single-customer deployment only. Running it as SaaS for multiple customers is a later problem.
- **Authentication and user management.** The MVP runs locally or on a single-customer server with no login. Add auth when you have customers.
- **Smart model routing.** All queries go to Claude Opus 4.6 for the MVP. Add Claude Haiku and open-source model routing at customer 3-5 when cost becomes a real issue.
- **Incremental updates.** The pipeline runs from scratch each time. Incremental ingest (only process new data) is a Week 6-8 feature, not Week 1-3.
- **Production deployment.** Runs on your laptop or a single cloud VM. Real deployment infrastructure comes with the first paying customer.
- **Caching.** First queries will be slow and expensive. Add caching after you have a customer asking the same questions repeatedly.
- **Fine-tuning, embeddings, vector search.** None of this is needed. The agent navigates the wiki directly, the way Karpathy describes. Don't add complexity you don't need.

The point of the MVP is to prove the architecture works and produce a demo that closes a customer. Everything else is premature.

---

## One Decision You'll Face Immediately

How much "structure" to impose on the wiki ingest. There are two extremes:

1. **Fully LLM-driven:** Feed the LLM raw ERP data and a prompt saying "make this a wiki." Let it decide what pages to make and how to link them. Maximum flexibility, minimum predictability, and the results vary run-to-run.

2. **Fully templated:** Write Python code that says "for every SKU row, create a page with these exact sections and these exact links." Maximum control, minimum flexibility, and you're basically back to writing a custom schema.

The right answer for HVAC distribution is somewhere in the middle, and specifically closer to templated than fully LLM-driven. HVAC distributor data has predictable shape — SKUs are always SKUs, suppliers are always suppliers. You get consistency and demo reliability by templating the main entity types. Then you let the LLM be more creative with the concept pages (cross-cutting things like "refrigerant exposure" or "tariff impact") and with the narrative text inside each page.

This is also what makes the pipeline productizable across customers. Templates transfer; pure LLM creativity doesn't.

Start with templates. Add LLM creativity only where templates can't express what you need.
