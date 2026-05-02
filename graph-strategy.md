# Graph: The HVAC Wedge

## The Big Picture

Graph is building LLM-native operational intelligence for mid-market companies whose data is a mess. The product is a living wiki of your entire business operations — ingested from your existing systems, maintained automatically by AI agents, and queryable in natural language by anyone on your team. The underlying architecture is the Karpathy-pattern LLM wiki (markdown files with backlinks that LLM agents navigate) hybridized with a structured data layer (DuckDB) for high-volume tabular data. This is genuinely new — nobody has productized this architecture for mid-market operations yet.

The opening wedge is HVAC. Specifically: PE-backed HVAC parts wholesale and distribution platforms that are integrating multiple bolt-on acquisitions. HVAC won the trade comparison on every dimension that matters — most fragmented mid-market distribution base, most active PE rollup activity at exactly the target customer profile, cleanest parts ontology to template around, and the strongest bridge to downstream service rollups (the largest PE consolidation play in the country right now).

Start with HVAC distribution. Use those case studies to move into HVAC service rollups. Then replicate the playbook in plumbing, then expand to other industrial verticals.

---

## The Technology Bet

The core technical decision is that we're not building a classic knowledge graph. Graph databases, ontologies, and ETL pipelines are the 2018 answer to this problem. They're slow to build, rigid when customer data is weird (which it always is), and require weeks of custom work per customer. The 2025 answer, made possible by frontier LLMs finally getting good enough at long-context reasoning and tool use, is the LLM-native wiki: raw data is ingested into a folder, an LLM compiles it into a structured markdown wiki with backlinks, and LLM agents navigate the wiki to answer questions, extend it with new data, and run health checks.

The one refinement on the pure Karpathy pattern is that operational data splits cleanly into two kinds. Knowledge (relationships, substitutes, supplier contacts, product descriptions, failure patterns, tribal knowledge) is what the wiki is great at. Facts (inventory counts, order history, prices, dates, numeric quantities) are what SQL is great at. Our architecture uses the wiki as the primary interface and the system-of-record for knowledge, but puts DuckDB underneath it for high-volume tabular data. Agents read the wiki for context and run SQL queries for numbers. This hybrid keeps the wiki small enough for LLMs to navigate efficiently while handling distributor-scale data volumes cleanly.

Key architectural decisions:

- **Wiki layer:** markdown files with backlinks, compiled and maintained by LLM agents. This is the knowledge system-of-record.
- **Structured layer:** DuckDB mirroring the customer's ERP tables for high-volume tabular data. Agents query it as a tool.
- **Agent layer:** LLM agents with a toolkit (read_wiki, search_wiki, run_sql, web_search, etc.). A router decides which model handles which query to control costs.
- **Audit layer:** every agent action logged with a full trace. Users can click "show sources" on any answer and see exactly which files and queries produced it. Solves the PE operating partner's trust concern directly.
- **Viewer layer:** Obsidian for direct browsing, custom web UI for chat queries.
- **Inference:** hosted APIs only (Anthropic first, add Together/Fireworks routing around customer 3-5 for cost control). Self-hosted GPUs are deferred indefinitely — possibly forever — because the ops burden isn't worth it until spend crosses $50k+/month.

This architecture is 3-4x faster to MVP than the classic graph database approach, handles messy real-world data natively, demos dramatically better ("your business as a living wiki that writes itself and answers any question" is a much stronger pitch than "a graph database with a chat UI"), and positions the company as an LLM-native 2025 story rather than a graph-database 2018 story. It's also the right architecture for the YC pitch — "riding the curve up" as frontier model capabilities improve.

---

## Phase 1: HVAC Parts Wholesale & Distribution

### The customer
PE-owned HVAC distribution platforms doing $50M–$500M in revenue that have completed 2–5 bolt-on acquisitions and are feeling integration pain. Think Team Air Distributing (Kian Capital), Shearer Supply (Investcorp), Hills Distribution-style platforms, and the dozens of other regional HVAC distributors that PE firms have rolled up over the last 3 years. Also relevant: master distributors like Global/MARS (Platinum Equity) and Everflow-style multi-trade distributors with significant HVAC exposure.

The buyer is the PE operating partner who owns the distribution thesis at the firm, plus the platform CEO they installed. These are practical, ROI-focused buyers who can sign contracts in weeks, not quarters. They have real money — typical PE platform builds run on $100M+ of equity — and they value integration work directly because it's the basis of their investment thesis.

### The problem
When a PE firm buys five regional HVAC distributors in the Southeast, they inherit five different ERPs (some mix of DDI System, Epicor Eclipse, Infor SX.e, and the occasional homegrown system), five different parts catalogs with overlapping but inconsistent SKUs, five different customer databases, five purchasing systems, and five sets of supplier relationships. The PE thesis depends on operational synergies — better purchasing power, cross-warehouse inventory visibility, unified customer pricing — but those synergies are stuck behind data integration that nobody on the operating team knows how to do.

Meanwhile, the world keeps changing. Refrigerants get phased out (HFC phase-down is hitting now). Tariffs shift. A major manufacturer like Lennox or Carrier changes pricing or allocations. When any of this happens, the platform spends 2–3 weeks manually figuring out exposure — which warehouses have what, which customers buy the affected SKUs, what the substitutes are, what the lead time impact looks like. Every disruption is a fire drill.

### What we deliver
A living wiki of the distributor's entire operation, automatically ingested from their ERPs and supporting systems, maintained by LLM agents, and queryable in natural language. The wiki contains pages for every SKU, supplier, manufacturer, customer, warehouse, and contract, with backlinks between them. Underneath it, a DuckDB instance mirrors the customer's tabular data (orders, inventory, transactions) for precise numeric queries.

The user experience: a chat interface for quick questions ("which customers buy R-410A equipment and what's our total exposure?"), a set of prebuilt dashboards for common recurring reports, and Obsidian access for direct browsing of the wiki. Every answer the chat produces includes a "show sources" button that surfaces the full audit trace — which files the agent read, which SQL queries it ran, which numbers it pulled.

The wiki is self-maintaining. When new data arrives (nightly ERP export, supplier email, updated manufacturer price sheet), agents update the relevant pages and add new ones. Health-check agents run periodically to flag inconsistencies and suggest new articles.

The pitch in one sentence: "The next time a tariff hits or a refrigerant phases out, you'll know your full exposure in 30 seconds instead of 3 weeks — and every answer is fully auditable down to the source data."

### The engagement model
Initial deployment: 4–6 weeks, $150k–$250k fixed fee. Two engineers working hybrid (on-site for kickoff and key milestones, remote otherwise). Because the architecture is wiki-first rather than custom schema design, deployment is dramatically faster than a classic graph-database approach — the first customer is 4-6 weeks, subsequent customers drop to 2-3 weeks as the pipeline matures.

Ongoing: $8k–$15k/month maintenance contract. Covers the living wiki (agents updating it as data flows in), model inference costs, hosting, health checks, and minor ontology tuning. Every new bolt-on acquisition the platform makes is an upsell — $20k–$40k to ingest the new company's data into the wiki.

The recurring revenue is the whole game. The initial fee covers the engagement cost; the monthly maintenance is where the margin and the long-term customer value live.

### Go-to-market

**Where to find customers.**
1. **HARDI** (Heating, Air-conditioning & Refrigeration Distributors International) is the trade association for HVAC distributors and has an active M&A community. Annual conference, regional meetups, and a published vendor directory. This is the single best entry point — sponsor a session, present at the M&A track, or just attend and meet operating partners.
2. **Named PE firms publicly active in HVAC distribution rollups:** Kian Capital (Team Air Distributing), Platinum Equity (Global/MARS), Investcorp (Shearer Supply), Grove Mountain Partners (Hills Distribution), Caymus Equity (recent commercial HVAC exits), Paceline Equity (Everflow), Novacap/Master Group (Refrigeration Sales Corp). Cold outreach to operating partners with "Distribution" or "Industrials" in their title.
3. **PE operating partner conferences** — ACG, Operating Partner Forum, and the various industrial-focused PE events. Operating partners talk to each other constantly, and one good conversation produces three intros.
4. **Industry publications** — ACHR News, Distribution Strategy Group, and Electrical Wholesaling all cover HVAC distribution M&A and have engaged readerships of exactly the buyers you want.

**The first deal.**
First customer is free or half-price ($50k–$100k) in exchange for a public case study, a quotable testimonial from the PE operating partner, and three reference intros. The goal is not revenue — it's the case study and the references. Pick a platform that has done 3–5 bolt-ons recently (visible integration pain), has a tech-friendly operating partner (some PE firms are openly anti-tech), and is small enough that you can deliver a perfect outcome with one engagement.

The wiki-first architecture enables a specific sales tactic that the classic graph approach can't: offer a 48-hour proof of concept. "Give us your data under NDA on Monday, we'll show you your own wiki on Wednesday." This is only possible because the pipeline is LLM-driven rather than custom-schema work. Use it aggressively — it's the single best demo you have.

**The next four deals.**
Sell at full price ($150k–$250k) using the case study. By the fifth engagement you have a real pipeline template, reusable connectors for the top 3 HVAC ERPs, a sales deck with hard ROI numbers, and a referenceable customer list. Deployment time drops from 4-6 weeks to 2-3 weeks.

**Why the PE network compounds.**
Once one operating partner at one PE firm has a positive experience, two things happen. First, they introduce you to their other distribution portfolio companies (most PE firms have 3–8 portcos in adjacent categories). Second, they mention you to peer operating partners at other PE firms — this world is small and operating partners trade vendor recommendations constantly. By customer 5, lead flow should be mostly inbound.

### Why HVAC distribution is the right place to start

HVAC parts ecosystems are the most templatable of the trades. Capacitors, contactors, motors, refrigerants, coils, control boards, thermostats — the parts catalog is finite, well-cataloged across manufacturers, and shared across distributors. Compare to electrical, where SKU counts run into the millions across wildly diverse product lines, or plumbing, which has complicated regional code variations. One template for HVAC distribution can serve hundreds of customers.

The buyer profile is the easiest on the entire mid-market opportunity list. PE operating partners are sophisticated enough to understand the value but practical enough to sign a contract without enterprise procurement theater. They control budget directly. They have a clear ROI lens. They are explicitly looking for ways to make their roll-ups work better.

The PE rollup activity in HVAC is the most intense in any industry right now. Per WSJ, PE has bought nearly 800 HVAC, plumbing, and electrical companies since 2022, and HVAC is the largest share. Apex Service Partners alone has done 107 acquisitions. Every one of those rolled-up companies is a potential downstream customer once you've built credibility on the distribution side.

### Risks

**Inference cost at scale.** The LLM wiki architecture depends on agent loops that read multiple files per query. At 50 employees asking 20 questions a day, naive implementation can cost $5k-15k per customer per month in API fees. Mitigation: smart model routing from day one, caching, pre-computed summaries, and aggressive prompt engineering. Costs come down significantly over time as frontier models get cheaper (they have been dropping roughly 10x per year) and as we shift routine queries to cheaper open-source models on Together/Fireworks.

**Scaling the wiki to distributor data volumes.** A large distributor has 50k SKUs, 10k customers, and years of order history. Pure wiki would struggle. The hybrid with DuckDB handles this — numbers live in SQL, knowledge lives in the wiki, the wiki stays small enough for efficient LLM navigation. Still, there's real engineering work around partitioning, pre-computed summaries, and agent query planning.

**Non-determinism and trust.** Some buyers will ask "how do I know this answer is right?" The audit layer solves this — every answer includes a full trace of what the agent read and what queries it ran. Citations and transparent reasoning are the answer, not pretending the LLM is deterministic.

**ServiceTitan, BuildOps, Watsco.** Existing HVAC-adjacent software vendors could in theory build competing products. They probably won't soon — they're focused on workflow automation and distribution commerce, not intelligence — but the threat is real. Positioning as "the intelligence layer that sits on top of your existing systems, not a replacement" is the right framing. Speed matters: establish the category before they wake up.

**Services-to-software transition.** The first 5-10 customers look like services engagements. If we don't productize quickly, we end up as a consultancy. Mitigation: the wiki architecture is inherently more productizable than custom schemas because the pipeline is reusable across customers — the transition is built into the technology choice, not bolted on later.

---

## Phase 2: HVAC Service Rollups

### When to start
Month 13–18, after 5–8 HVAC distribution case studies and at least 2 strong PE operating partner references. Don't try to do this in parallel with phase 1 — splitting focus too early will dilute both.

### The customer
PE-backed HVAC contractor rollups. The biggest names: Apex Service Partners (Alpine Investors), Wrench Group (Leonard Green), Service Champions (Odyssey), Sila Services, Redwood Services, Goettl. There are dozens more at smaller scale. These platforms have acquired anywhere from 5 to 100+ local HVAC contractors and are trying to make them operate as one company.

### The problem
Every problem from the distribution side, plus a layer the distributors don't have: technician knowledge. When a PE-backed HVAC service platform buys 12 local contractors, they inherit not just 12 different field service software systems (mix of ServiceTitan, FieldEdge, BuildOps, and legacy tools) but 12 different cultures of tribal knowledge that lives in the heads of veteran technicians. First-time-fix rate is the metric that drives profitability in this business, and the difference between an experienced tech and a junior tech is access to historical context: "has anyone in any of our 12 companies seen this exact issue on this exact unit at this exact customer before."

### The graph
The same wiki-plus-DuckDB architecture, extended with technician, equipment, and work-order concepts. The parts ontology from phase 1 is directly reusable — 60-70% of the wiki schema transfers. You're extending the same template to a new use case, not building from scratch.

The technician-facing interface is critical here. A technician in the field opens the app on their phone at a customer site, asks "anyone seen this exact failure on this model before," and gets an answer that cites specific past work orders from across the platform's acquired companies. That's a direct first-time-fix-rate improvement, which is directly a profit improvement for the PE platform.

### The engagement model
Two-phase engagement structure. Phase 1 is integration ($200k–$350k, 6–8 weeks) where you unify the data from acquired companies into one wiki. Phase 2 is intelligence ($15k–$25k/month ongoing) where you maintain the wiki, add new acquisitions as they come in, and provide the technician-facing query interface.

Phase 2 recurring revenue is the whole game. Every new acquisition is an automatic upsell, and these platforms acquire constantly.

### How phase 1 enables phase 2
The PE firms doing HVAC distribution rollups overlap heavily with the PE firms doing HVAC service rollups. Some firms own both. Many operating partners at the firm level cover the entire HVAC vertical regardless of where in the value chain a portco sits. By the time you've done 5–8 HVAC distribution engagements, you'll know operating partners who can introduce you directly to their service rollup portcos.

Even when there's no direct overlap, the credibility transfer is huge. "We've done living operational wikis for five PE-backed HVAC platforms including [named references]" opens doors that cold outreach never could.

---

## The 18-Month Plan

**Months 1–2:** Build the MVP — wiki compilation pipeline, agent toolkit, DuckDB integration, audit logging, chat UI. Synthesize realistic HVAC distributor data to demo against. Goal: a 2-minute demo video and a working 48-hour pilot offer.

**Months 2–3:** Attend HARDI's next major event. Begin outbound to named PE operating partners. Run the 48-hour pilot offer aggressively — "give us your data, we'll show you your wiki in 2 days." Close first customer at half-price in exchange for case study.

**Months 4–9:** Sell 3–5 HVAC distribution engagements at full price. Build out the pipeline template, hire 1–2 more engineers. Start writing publicly about HVAC distribution data problems (LinkedIn, ACHR News guest pieces) to build inbound pipeline. Add smart model routing to bring inference costs down.

**Months 10–12:** Reach $1M+ in committed revenue between engagements and maintenance. Begin conversations with HVAC service rollup operating partners using distributor case studies as proof.

**Months 13–18:** Land first HVAC service rollup engagement. Build out the technician/equipment/work-order extensions to the existing wiki template. Use distribution revenue to fund the longer service rollup sales cycles.

**Month 18 checkpoint:** Two reusable pipeline templates (HVAC distribution and HVAC service), 8–12 customer case studies, recurring maintenance revenue covering fixed costs, and a PE network producing inbound deal flow in both segments. Foundation set for YC application (if not already applied) and for scaling into adjacent verticals.

---

## The One Thing That Matters Most

Pick the first customer carefully. The first engagement is not about revenue — it's about building a perfect case study with a quotable PE operating partner who will introduce you to peers. Spend 60 days finding the right first customer rather than 30 days finding the wrong one. Criteria: PE-owned HVAC distribution platform, 3–5 recent bolt-ons, tech-friendly operating partner, small enough to deliver flawlessly, big enough to be credible as a reference.

Everything else flows from getting that first deal right.
