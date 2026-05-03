/* Graph chat client.
 *
 * - Streams the agent loop via SSE (POST /chat/stream)
 * - Falls back to non-streaming POST /chat if the stream fails
 * - GET /audit/{trace_id} for the audit drawer (lazy)
 * - Self-contained markdown renderer (no external deps)
 * - Auto-growing textarea, Enter to send, Shift+Enter for newline
 * - Drawer for the audit trace with formatted per-step display
 */

(() => {
    "use strict";

    const form = document.getElementById("composer");
    const input = document.getElementById("question");
    const sendBtn = document.getElementById("send-button");
    const messages = document.getElementById("messages");
    const empty = document.getElementById("empty-state");
    const conversation = document.getElementById("conversation");

    const drawer = document.getElementById("sources-panel");
    const drawerBody = document.getElementById("sources-body");
    const drawerTitle = document.getElementById("sources-title");
    const drawerClose = document.getElementById("sources-close");
    const drawerScrim = document.getElementById("sources-scrim");

    let inFlight = false;

    /* ---- Minimal markdown renderer (no external dep) ----
     *
     * Handles what the agent typically produces: headings, bold/italic,
     * inline + fenced code, links, bullet/numbered lists, GitHub-style
     * pipe tables, paragraphs. Stays under 80 lines. Escapes HTML by
     * default so we never inject raw markup.
     */
    const escapeHTML = (s) => String(s).replace(/[&<>"']/g, (c) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));

    const renderInline = (text) => {
        let s = escapeHTML(text);
        s = s.replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`);
        s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
        s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
        s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, h) =>
            `<a href="${h}" target="_blank" rel="noopener">${t}</a>`);
        return s;
    };

    const renderTable = (lines) => {
        // lines: [header, separator, ...rows]
        const cells = (line) => line.replace(/^\||\|$/g, "").split("|").map(c => c.trim());
        const headers = cells(lines[0]);
        const body = lines.slice(2).map(cells);
        const th = headers.map(h => `<th>${renderInline(h)}</th>`).join("");
        const trs = body.map(row =>
            `<tr>${row.map(c => `<td>${renderInline(c)}</td>`).join("")}</tr>`).join("");
        return `<table><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table>`;
    };

    const renderMarkdown = (text) => {
        const lines = text.replace(/\r\n/g, "\n").split("\n");
        const out = [];
        let i = 0;
        while (i < lines.length) {
            const line = lines[i];
            // fenced code
            if (/^```/.test(line)) {
                const buf = [];
                i++;
                while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
                i++; // skip closing fence
                out.push(`<pre><code>${escapeHTML(buf.join("\n"))}</code></pre>`);
                continue;
            }
            // heading
            const h = line.match(/^(#{1,3})\s+(.*)$/);
            if (h) {
                out.push(`<h${h[1].length}>${renderInline(h[2])}</h${h[1].length}>`);
                i++; continue;
            }
            // table: header line + separator line of |---|---|
            if (/^\|.*\|/.test(line) && i + 1 < lines.length && /^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$/.test(lines[i + 1])) {
                const tlines = [line, lines[i + 1]];
                let j = i + 2;
                while (j < lines.length && /^\|.*\|/.test(lines[j])) tlines.push(lines[j++]);
                out.push(renderTable(tlines));
                i = j; continue;
            }
            // unordered list
            if (/^\s*[-*]\s+/.test(line)) {
                const items = [];
                while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
                    items.push(lines[i].replace(/^\s*[-*]\s+/, ""));
                    i++;
                }
                out.push(`<ul>${items.map(it => `<li>${renderInline(it)}</li>`).join("")}</ul>`);
                continue;
            }
            // ordered list
            if (/^\s*\d+\.\s+/.test(line)) {
                const items = [];
                while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
                    items.push(lines[i].replace(/^\s*\d+\.\s+/, ""));
                    i++;
                }
                out.push(`<ol>${items.map(it => `<li>${renderInline(it)}</li>`).join("")}</ol>`);
                continue;
            }
            // blank line
            if (line.trim() === "") { i++; continue; }
            // paragraph (collect consecutive non-block lines)
            const buf = [line];
            i++;
            while (i < lines.length
                   && lines[i].trim() !== ""
                   && !/^```/.test(lines[i])
                   && !/^#{1,3}\s/.test(lines[i])
                   && !/^\s*[-*]\s/.test(lines[i])
                   && !/^\s*\d+\.\s/.test(lines[i])) {
                buf.push(lines[i++]);
            }
            out.push(`<p>${renderInline(buf.join(" "))}</p>`);
        }
        return out.join("\n");
    };

    /* ---- Auto-grow textarea ---- */
    const autosize = () => {
        input.style.height = "auto";
        input.style.height = `${Math.min(input.scrollHeight, 220)}px`;
    };
    input.addEventListener("input", autosize);

    /* ---- Empty state suggestions ---- */
    document.querySelectorAll(".suggested-card").forEach((btn) => {
        btn.addEventListener("click", () => {
            input.value = btn.dataset.q;
            autosize();
            input.focus();
            form.requestSubmit();
        });
    });

    /* ---- Submit ---- */
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (inFlight) return;
        const question = input.value.trim();
        if (!question) return;

        empty.classList.add("hidden");
        appendUserMessage(question);
        input.value = "";
        autosize();
        inFlight = true;
        sendBtn.disabled = true;

        const renderer = createStreamingRenderer();
        try {
            await streamChat(question, renderer);
        } catch (err) {
            renderer.fail(err.message || String(err));
        } finally {
            inFlight = false;
            sendBtn.disabled = false;
            input.focus();
        }
    });

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
            event.preventDefault();
            form.requestSubmit();
        }
    });

    /* ---- Stream POST /chat/stream and feed events to a renderer ---- */
    const streamChat = async (question, renderer) => {
        const res = await fetch("/chat/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
            body: JSON.stringify({ question }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            renderer.fail(err.detail || `Request failed (${res.status})`);
            return;
        }
        // Some hosts don't expose ReadableStream — fall back to JSON.
        if (!res.body) {
            const data = await res.json();
            renderer.complete(data.answer, data.trace_id, data.iterations);
            return;
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            // SSE events are separated by blank lines.
            let idx;
            while ((idx = buffer.indexOf("\n\n")) >= 0) {
                const raw = buffer.slice(0, idx);
                buffer = buffer.slice(idx + 2);
                const dataLine = raw.split("\n").find((l) => l.startsWith("data:"));
                if (!dataLine) continue;
                let payload;
                try {
                    payload = JSON.parse(dataLine.slice(5).trim());
                } catch {
                    continue;
                }
                renderer.event(payload);
            }
        }
    };

    /* ---- Streaming renderer: builds the assistant message in-place ---- */
    const createStreamingRenderer = () => {
        const wrap = document.createElement("div");
        wrap.className = "msg msg-assistant streaming";
        wrap.innerHTML = `
            <span class="msg-role">Graph</span>
            <div class="msg-progress">
                <div class="progress-row">
                    <span class="thinking-dots"><span></span><span></span><span></span></span>
                    <span class="progress-text">Thinking…</span>
                </div>
                <ul class="progress-steps"></ul>
            </div>
            <div class="msg-body" hidden></div>
            <div class="msg-meta" hidden>
                <button class="show-sources" type="button">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M9 18h6"></path><path d="M10 22h4"></path>
                        <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"></path>
                    </svg>
                    Show sources
                </button>
                <span class="iter-badge"></span>
            </div>
        `;
        const progress = wrap.querySelector(".msg-progress");
        const progressText = wrap.querySelector(".progress-text");
        const stepsList = wrap.querySelector(".progress-steps");
        const body = wrap.querySelector(".msg-body");
        const meta = wrap.querySelector(".msg-meta");
        const sourcesBtn = wrap.querySelector(".show-sources");
        const iterBadge = wrap.querySelector(".iter-badge");

        messages.appendChild(wrap);
        scrollToBottom();

        let traceId = null;

        const appendStep = (label, detail) => {
            const li = document.createElement("li");
            li.className = "progress-step";
            li.innerHTML = `<span class="step-label">${escapeHTML(label)}</span>` +
                           (detail ? `<span class="step-detail">${escapeHTML(detail)}</span>` : "");
            stepsList.appendChild(li);
            scrollToBottom();
        };

        return {
            event(ev) {
                switch (ev.kind) {
                    case "started":
                        traceId = ev.trace_id;
                        progressText.textContent = "Reading the wiki and querying your data…";
                        break;
                    case "tool_call": {
                        const summary = ev.name === "run_sql"
                            ? `${(ev.input.query || "").slice(0, 80).replace(/\s+/g, " ")}…`
                            : ev.name === "read_wiki_page" ? ev.input.path
                            : ev.name === "search_wiki"    ? `"${ev.input.query}"`
                            : ev.name === "list_wiki_directory" ? ev.input.directory || "/"
                            : "";
                        appendStep(ev.name, summary);
                        break;
                    }
                    case "iteration":
                        progressText.textContent = `Step ${ev.iteration}…`;
                        break;
                    case "final":
                        wrap.classList.remove("streaming");
                        progress.remove();
                        body.hidden = false;
                        meta.hidden = false;
                        body.innerHTML = renderMarkdown(ev.answer || "(no answer)");
                        iterBadge.textContent = `${ev.iterations} step${ev.iterations === 1 ? "" : "s"} · trace ${(ev.trace_id || traceId || "").slice(-8)}`;
                        sourcesBtn.addEventListener("click", () => openSources(ev.trace_id || traceId));
                        scrollToBottom();
                        break;
                    case "error":
                        this.fail(ev.message || "Unknown error");
                        break;
                    default:
                        break;
                }
            },
            complete(answer, tid, iterations) {
                this.event({ kind: "final", answer, trace_id: tid, iterations });
            },
            fail(message) {
                wrap.classList.remove("streaming");
                wrap.classList.remove("msg-assistant");
                wrap.classList.add("msg-error");
                progress.remove();
                body.hidden = false;
                meta.hidden = true;
                body.textContent = message;
                scrollToBottom();
            },
        };
    };

    /* ---- Message helpers ---- */
    const scrollToBottom = () => {
        conversation.scrollTop = conversation.scrollHeight;
    };

    const appendUserMessage = (text) => {
        const wrap = document.createElement("div");
        wrap.className = "msg msg-user";
        wrap.innerHTML = `<span class="msg-role">You</span><div class="msg-body"></div>`;
        wrap.querySelector(".msg-body").textContent = text;
        messages.appendChild(wrap);
        scrollToBottom();
    };

    /* ---- Briefs drawer ---- */
    const briefsDrawer = document.getElementById("briefs-panel");
    const briefsBody = document.getElementById("briefs-body");
    const briefsTitle = document.getElementById("briefs-title");
    const briefsClose = document.getElementById("briefs-close");
    const openBriefsBtn = document.getElementById("open-briefs");

    const closeBriefs = () => {
        briefsDrawer.classList.remove("open");
        drawerScrim.classList.remove("visible");
        briefsDrawer.setAttribute("aria-hidden", "true");
    };

    const openBriefs = async () => {
        briefsTitle.textContent = "Daily brief";
        briefsBody.innerHTML = "<p class=\"brief-rendered\">Loading…</p>";
        briefsDrawer.classList.add("open");
        drawerScrim.classList.add("visible");
        briefsDrawer.setAttribute("aria-hidden", "false");
        try {
            const res = await fetch("/briefs");
            const briefs = await res.json();
            if (!Array.isArray(briefs) || briefs.length === 0) {
                briefsBody.innerHTML = `
                    <p class="brief-empty">
                        No briefs yet. Generate one with:
                        <br><br>
                        <code>python scripts/generate_brief.py</code>
                    </p>
                `;
                return;
            }
            // Show the most recent brief by default; list the rest below.
            const latest = briefs[0];
            const r = await fetch(`/briefs/${latest.date}`);
            const data = await r.json();
            renderBrief(data);

            if (briefs.length > 1) {
                const list = document.createElement("ul");
                list.className = "brief-list";
                list.style.marginTop = "24px";
                briefs.slice(1).forEach((b) => {
                    const li = document.createElement("li");
                    li.innerHTML = `<span>${b.date}</span><button data-date="${b.date}">View</button>`;
                    li.querySelector("button").addEventListener("click", async () => {
                        const r = await fetch(`/briefs/${b.date}`);
                        renderBrief(await r.json());
                    });
                    list.appendChild(li);
                });
                briefsBody.appendChild(list);
            }
        } catch (err) {
            briefsBody.innerHTML = `<p class="brief-empty">Couldn't load briefs: ${err.message}</p>`;
        }
    };

    const renderBrief = (data) => {
        const text = data.body || "";
        const fmMatch = text.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
        const frontmatter = fmMatch ? fmMatch[1] : "";
        const body = fmMatch ? fmMatch[2] : text;
        const fm = frontmatter
            ? `<div class="frontmatter">${escapeHTML(frontmatter)}</div>` : "";
        briefsTitle.textContent = `Brief — ${data.date}`;
        briefsBody.innerHTML = `<div class="brief-rendered">${fm}${renderMarkdown(body)}</div>`;
    };

    openBriefsBtn.addEventListener("click", openBriefs);
    briefsClose.addEventListener("click", closeBriefs);

    /* ---- Sources drawer ---- */
    const closeDrawer = () => {
        drawer.classList.remove("open");
        drawerScrim.classList.remove("visible");
        drawer.setAttribute("aria-hidden", "true");
        drawerScrim.setAttribute("aria-hidden", "true");
    };

    const closeAnyDrawer = () => {
        if (drawer.classList.contains("open")) closeDrawer();
        if (briefsDrawer.classList.contains("open")) closeBriefs();
    };

    drawerClose.addEventListener("click", closeDrawer);
    drawerScrim.addEventListener("click", closeAnyDrawer);
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeAnyDrawer();
    });

    const openSources = async (traceId) => {
        if (!traceId) return;
        drawerTitle.textContent = "Loading…";
        drawerBody.innerHTML = "";
        drawer.classList.add("open");
        drawerScrim.classList.add("visible");
        drawer.setAttribute("aria-hidden", "false");
        drawerScrim.setAttribute("aria-hidden", "false");

        try {
            const res = await fetch(`/audit/${encodeURIComponent(traceId)}`);
            if (!res.ok) {
                drawerBody.innerHTML = `<p style="color:var(--danger);padding:24px 0;">Couldn't load trace: ${res.statusText}</p>`;
                return;
            }
            const trace = await res.json();
            renderTrace(trace, traceId);
        } catch (err) {
            drawerBody.innerHTML = `<p style="color:var(--danger);padding:24px 0;">Network error: ${err.message}</p>`;
        }
    };

    const formatPayload = (kind, payload) => {
        const truncate = (s, n) => (s.length > n ? `${s.slice(0, n)}\n… (${s.length - n} more chars)` : s);

        if (kind === "user_question") {
            return `<span class="label">Question</span>${escapeHTML(payload.question || "")}\n` +
                   `<span class="label">Model</span>${escapeHTML(payload.model || "")}`;
        }
        if (kind === "tool_call") {
            const args = JSON.stringify(payload.input, null, 2);
            return `<span class="label">Tool</span><span class="trace-tool-name">${escapeHTML(payload.name)}</span>\n` +
                   `<span class="label">Input</span>${escapeHTML(args)}`;
        }
        if (kind === "tool_result") {
            return `<span class="label">From</span><span class="trace-tool-name">${escapeHTML(payload.name)}</span>\n` +
                   `<span class="label">Returned ${payload.result_length} chars</span>${escapeHTML(truncate(payload.result_preview || "", 1500))}`;
        }
        if (kind === "model_response") {
            const lines = [`<span class="label">Stop reason</span>${escapeHTML(payload.stop_reason || "")}`];
            const u = payload.usage || {};
            lines.push(`<span class="label">Usage</span>in=${u.input_tokens || 0}  out=${u.output_tokens || 0}  cache_read=${u.cache_read_input_tokens || 0}  cache_write=${u.cache_creation_input_tokens || 0}`);
            const text = (payload.content || []).filter(b => b.type === "text").map(b => b.text).join("\n").trim();
            if (text) lines.push(`<span class="label">Text</span>${escapeHTML(truncate(text, 800))}`);
            const tools = (payload.content || []).filter(b => b.type === "tool_use");
            if (tools.length) {
                lines.push(`<span class="label">Tool calls</span>${tools.map(t => `${t.name}(${JSON.stringify(t.input)})`).join("\n")}`);
            }
            return lines.join("\n");
        }
        return escapeHTML(JSON.stringify(payload, null, 2));
    };

    const labelForKind = (kind) => ({
        user_question: "Question received",
        model_response: "Model response",
        tool_call: "Tool call",
        tool_result: "Tool result",
        max_iterations_reached: "Max iterations reached",
    }[kind] || kind);

    const renderTrace = (trace, traceId) => {
        if (!Array.isArray(trace) || trace.length === 0) {
            drawerTitle.textContent = "Empty trace";
            drawerBody.innerHTML = "";
            return;
        }
        const counts = trace.reduce((acc, s) => {
            acc[s.kind] = (acc[s.kind] || 0) + 1;
            return acc;
        }, {});
        const summaryBits = [];
        if (counts.tool_call)     summaryBits.push(`${counts.tool_call} tool call${counts.tool_call === 1 ? "" : "s"}`);
        if (counts.model_response) summaryBits.push(`${counts.model_response} model response${counts.model_response === 1 ? "" : "s"}`);
        drawerTitle.textContent = summaryBits.join(" · ") || "Trace";

        drawerBody.innerHTML = trace.map((step) => `
            <div class="trace-step">
                <div class="trace-step-head">
                    <span class="trace-iter">${step.iteration}</span>
                    <span class="trace-kind kind-${step.kind}">${escapeHTML(labelForKind(step.kind))}</span>
                </div>
                <div class="trace-detail">${formatPayload(step.kind, step.payload)}</div>
            </div>
        `).join("");

        const footer = document.createElement("p");
        footer.style.cssText = "margin-top:24px;font-size:11px;color:var(--text-faint);font-family:var(--font-mono);";
        footer.textContent = `trace_id: ${traceId}`;
        drawerBody.appendChild(footer);
    };
})();
