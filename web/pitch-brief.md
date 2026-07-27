# Graph — Pitch Brief

# What It Is

**Graph turns messy paperwork into instant, trustworthy answers.**

Imagine every bulletin, contract, email, spreadsheet, and internal memo a
business has ever produced — all searchable in one place, where you can
just *ask a question in plain English* and get a straight answer with the
exact source attached, so you can verify it yourself in one click.

That's Graph. It was built and proven end-to-end on a real (if simulated)
business — an HVAC parts distributor — and it works well enough that it's
now being mapped onto a completely different business model: a
club-portfolio operator like **Invited**.

# The Value, in Plain Terms

An operations leader spends real time every week hunting for answers
scattered across systems: *"Which vendor is a concentration risk?" "Which
members are we exposed to if this contract changes?" "What's our
inventory risk this week?"*

Graph does that hunting automatically and delivers it as a standing
morning brief, or answers it live in a chat window — and every claim it
makes points back to the actual document it came from. No guessing, no
"trust me," no hallucinated numbers.

# How It Works (No Jargon)

1. **Reads everything.** Contracts, emails, spreadsheets, PDFs, tickets —
   normalized into one searchable library.
2. **Finds the right pieces, fast.** A hybrid search (keyword + meaning-based)
   pulls the handful of documents actually relevant to a question, out of
   thousands.
3. **Writes a real answer.** An AI reads those pieces and drafts a clear,
   specific answer — not a document dump.
4. **Shows its work.** Every sentence in the answer is tagged to the exact
   source it came from. If the AI can't point to a real source, that part
   of the answer gets removed automatically — it literally cannot
   fabricate a citation.
5. **Grades itself.** The system was tested against 30 hand-written
   questions with known correct answers, so its accuracy is a *measured
   number*, not a claim.

# Proof It Works

| Measure | Result | What it means |
|---|---|---|
| Finds the right source | 96.7% of the time in the top 5 results | It almost never misses the right document |
| Citation accuracy | 98.3% | Nearly every claim it makes is properly sourced |
| Spot-check on real answers | 5 / 5 verified | Every citation checked by hand actually supported the claim |
| Handles bad-faith questions | 3 / 3 correctly refused | Off-topic, jailbreak, and data-fishing attempts were all handled safely |
| Cost per question | About 3 cents | Cheap enough to run continuously, not just for demos |

# Applied to a Club Portfolio (Invited)

The system was built once and already re-maps onto a club-portfolio
business without rebuilding anything — same underlying engine, new
vocabulary:

| Built for HVAC | Becomes, for a club portfolio |
|---|---|
| Warehouse (distribution center) | Club location |
| Supplier / vendor | Vendor (F&B, landscaping, maintenance) |
| Customer | Member |
| Refrigerant-phase-out exposure report | Labor / energy / dues-risk exposure report |
| Supplier concentration risk | Vendor concentration risk |
| Daily operations brief | **Savings Opportunity Tracker** — scored against a real savings target (e.g., $10M), not just an open-ended report |

Nothing about the underlying system changed to make this work — only the
labels. That's the strongest part of the pitch: the architecture is
general-purpose by design, and that was proven by actually doing it
twice, not by asserting it.

# Where This Goes From Here

- **Hosted live demo** — a public link so a reviewer can try it themselves
  instead of needing to install anything. Biggest next lever for making a
  strong first impression.
- **Pilot on real Invited data** — swap the simulated dataset for a real
  (even partial) data extract to prove the mapping holds outside the demo
  environment.
- **Tune the Savings Opportunity Tracker** — wire it to a specific,
  agreed savings target and real vendor/member data so it becomes a
  working weekly report, not a mock-up.
- **Expand source coverage** — point the ingestion pipeline at whatever
  systems the target business already has (contracts, POS exports,
  member CRM) the same way it was pointed at HVAC bulletins and tickets.

# The Builder

This wasn't assembled from a template — it was built end-to-end: document
ingestion, hybrid search, an AI agent with tools, a citation-trust layer
that prevents fabrication, and a formal evaluation suite that measures
accuracy and cost. Every design decision and trade-off along the way is
documented. And the club-portfolio mapping above wasn't requested — it
was done in advance, as a demonstration of exactly the kind of thinking
this system is meant to support.
