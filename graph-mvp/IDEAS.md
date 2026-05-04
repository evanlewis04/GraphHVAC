# Graph MVP — Candidate Additions

A menu of things we could build next, sized roughly and grouped by what
they buy you. Pick what to do; nothing here is in flight yet.

Key:
- **Demo win** — visible to a PE buyer in a 10-minute demo
- **Trust** — strengthens the auditability/ROI story
- **Sales lever** — unlocks pricing power, faster pilots, or wider TAM
- **Foundation** — paves the way for later work

Sizes are rough engineering days for one good engineer.

---

## Tier 1 — High-leverage, MVP-sized (1–3 days each)

### A. Streaming chat responses (1–2 days) — *demo win* — **DONE**
The agent loop is now a generator that yields events; `POST /chat/stream`
emits them as SSE. The UI renders each tool call as it lands so the user
sees what the agent is doing instead of staring at a spinner. Shipped
with full audit-trail parity.

### B. Daily executive brief (2–3 days) — *demo win + sales lever* — **PARTIALLY DONE**
The generator + `data/briefs/YYYY-MM-DD.md` writer + `/briefs` endpoints
+ brief viewer drawer in the UI are built. Run with
`python scripts/generate_brief.py`. Email/Slack delivery is still pending
— pair this with #L below when wiring up Slack.

### C. Cost & latency dashboard (1 day) — *trust*
The audit log already records token usage and timing. Aggregate it into
a `/admin/usage` page: cost-per-query, cost-per-customer (when we have
multi-tenant), p50/p95 latency, cache hit rate. PE operating partners
respond well to operational dashboards on the tools they buy.

### D. Export answer to PDF / Excel (1 day) — *demo win*
A "Download" button on each answer that emits a one-page PDF report
(answer + citations) or an .xlsx of the supporting query results. Lets
buyers say "this is something I can forward." Native Python: `pypdf` /
`openpyxl`.

### E. Smart model routing (2 days) — *unit economics*
Today every query goes to `claude-opus-4-7`. Add a router that uses a
fast classifier (Haiku 4.5, ~$1/1M tokens) to pick the right tier:
factual-lookup → Haiku, multi-step reasoning → Opus. The strategy doc
calls this out as the cost-control move at customer 3-5; building the
shim now means the `router.pick_model()` slot is wired without changing
the rest of the loop.

### F. Vendored marked.js + offline mode (½ day) — *trust* — **DONE**
The chat UI now uses an inline 80-line markdown renderer (no CDN, no
vendored bundle, zero external deps). Works in any network environment.

---

## Tier 2 — Bigger investments, real product moves (4–10 days)

### G. Multi-tenant infrastructure (5–7 days) — *foundation, sales lever*
One Graph deployment serving multiple PE portcos. Adds: tenant ID on
every request, isolated wiki + DuckDB per tenant, per-tenant audit log,
per-tenant rate limit. Required before customer 2 if we don't want a
fleet of single-tenant boxes.

### H. Authentication + RBAC (3–4 days) — *foundation*
Right now anyone with the URL can chat. Add Auth0 / Clerk / WorkOS
(prefer WorkOS for the SAML hand-shake every PE platform demands), then
two roles: viewer and admin. Pairs naturally with multi-tenant.

### I. Real ERP connector — DDI System (5–8 days) — *sales lever*
Every HVAC distributor in the target list runs DDI, Eclipse, or SX.e.
DDI is the most common. A real connector (read-only) replaces CSV uploads
with a nightly sync. Customer-specific work that becomes the template
for the next two ERPs.

### J. Incremental wiki updates (4–5 days) — *foundation*
Today the compiler rewrites every page on every run. With 50K SKUs this
won't scale. Add row-version tracking so we only re-compile pages whose
upstream data changed. Cuts re-compile from minutes to seconds, makes
nightly delta-syncs feasible.

### K. Health-check agent (3–4 days) — *trust*
A scheduled agent that samples 30 wiki pages, asks Claude "anything
inconsistent or out of date?", writes findings to `concepts/health-check.md`.
Demonstrates the "wiki maintains itself" pitch concretely.

### L. Slack integration (3–4 days) — *demo win*
A `/graph` Slack slash-command that runs the agent and posts the answer
inline, with a "Show sources" button that links back to the audit
trace. PE operating partners live in Slack with their portcos.

---

## Tier 3 — Polish + nice-to-haves (1–3 days each)

### M. Saved queries / query history per user
A sidebar of recent questions with click-to-rerun and pin-to-pinned.

### N. Keyboard cmd-k palette
Linear-style cmd-k that lets the user jump to wiki entities by name
without typing a question.

### O. Custom Obsidian theme for the vault
A small `.obsidian/themes/graph.css` that matches our brand. Makes the
"open the vault" portion of the demo look polished without writing a
custom viewer.

### P. Concept-page autogeneration on a schedule
The current concept pages are a fixed list (`r-410a-phase-out`,
`supplier-concentration`, `top-customers-by-revenue`). A nightly agent
could propose new concept pages when it spots interesting patterns
(e.g., "Lennox order volume dropped 30% in the last 60 days").

### Q. Per-customer system prompt customization
A small admin UI to tweak the system prompt per tenant ("our distributor
is a Lennox PartsPlus member; weight Lennox SKUs accordingly").

### R. Tone / "voice of the customer" guide
Short style guide for the answers — when to be terse, when to elaborate,
how to handle "I don't know." Pairs with prompt iteration after the
first 5 customer queries.

---

## Tier 4 — Long-horizon ($$$, weeks)

### S. Vector search layer
Embeddings over wiki pages for fuzzy-match queries Claude's substring
search can't handle. Defer until a real customer asks.

### T. Self-hosted inference (vLLM + Llama 3.x or Qwen 2.5 on H100)
The strategy doc explicitly defers this until $50K+/month inference spend.

### U. Phase 2: HVAC service rollups
The technician-facing field-service interface, work-order ingestion,
"has anyone seen this exact failure" search. Per the strategy doc this
starts month 13–18.

### V. Phase 3: Plumbing + electrical templates
Ontology adaptation. Big lift, big TAM unlock.

---

## My recommendations, if you want a starting list

**Done in this session:** A (streaming), F (offline markdown), B (brief
generator + viewer; email/Slack delivery still pending).

Next, in order:

1. **D. PDF export** — pairs with B for the "send this to the CEO" use case
2. **L. Slack integration** — completes B by actually delivering the brief
3. **C. Cost & latency dashboard** — leverages the audit-trail data we already record
4. **K. Health-check agent** — concrete demonstration of the "self-maintaining" pitch

Before customer #2:

5. **H. Auth** + **G. Multi-tenant** (tied; do together)
6. **I. Real ERP connector** (DDI first) — required to leave CSV-upload land
7. **J. Incremental wiki updates** — needed once a real customer has 50K+ SKUs

Would also do small Obsidian theme polish (#O) before any HARDI demo
specifically — a 1-day item that punches above its weight.
