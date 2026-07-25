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

    /* ---- Citation rendering --------------------------------------------- */
    // Turn every "[c1]" text occurrence into a clickable footnote span.
    const decorateCitations = (html, citations) => {
        if (!citations || citations.length === 0) return html;
        const known = new Set(citations.map((c) => c.id));
        // Walk attribute-safe regions only; the markdown renderer escapes
        // user content, so a global string replace is safe here.
        return html.replace(/\[c(\d+)\]/g, (m, n) => {
            const cid = `c${n}`;
            if (!known.has(cid)) return m;
            return `<a class="cite-ref" href="#${cid}" data-cid="${cid}">[${cid}]</a>`;
        });
    };

    const renderCitationCards = (citations) => {
        const cards = citations.map((c) => {
            const head = (c.heading_path || []).join(" › ");
            const pageBit = c.page_range && c.page_range[0] >= 0
                ? ` · p.${c.page_range[0]}${c.page_range[0] !== c.page_range[1] ? `–${c.page_range[1]}` : ""}`
                : "";
            const bucket = c.bucket ? `<span class="cite-bucket">${escapeHTML(c.bucket)}</span>` : "";
            return `
                <div class="cite-card" id="${c.id}" data-cid="${c.id}" data-source-id="${escapeHTML(c.source_id)}">
                    <div class="cite-card-head">
                        <span class="cite-card-id">${c.id}</span>
                        ${bucket}
                        <span class="cite-card-source">${escapeHTML(c.source_id)}</span>
                    </div>
                    ${head ? `<div class="cite-card-heading">${escapeHTML(head)}${pageBit}</div>` : ""}
                    <div class="cite-card-snippet">${escapeHTML(c.snippet || "")}</div>
                    <div class="cite-card-footer">
                        <span class="cite-card-score">score ${(c.score || 0).toFixed(2)}</span>
                        <button type="button" class="cite-open-source">Open source</button>
                    </div>
                    <pre class="cite-card-expand" hidden></pre>
                </div>
            `;
        }).join("");
        return `<div class="citations-title">Citations</div>${cards}`;
    };

    const wireCitationLinks = (root, citations) => {
        const byId = new Map((citations || []).map((c) => [c.id, c]));
        root.querySelectorAll(".cite-ref").forEach((link) => {
            const cid = link.dataset.cid;
            const c = byId.get(cid);
            // Hover preview (Phase 7) — title attribute as fallback, custom popover as primary.
            if (c) {
                const head = (c.heading_path || []).join(" › ");
                link.title = `${c.source_id}${head ? "\n" + head : ""}\n\n${c.snippet || ""}`;
                link.addEventListener("mouseenter", (e) => showCitationPopover(e, c));
                link.addEventListener("mouseleave", hideCitationPopover);
            }
            link.addEventListener("click", (e) => {
                e.preventDefault();
                hideCitationPopover();
                const target = root.querySelector(`.cite-card[data-cid="${cid}"]`);
                if (!target) return;
                target.scrollIntoView({ behavior: "smooth", block: "center" });
                target.classList.add("flash");
                setTimeout(() => target.classList.remove("flash"), 1500);
            });
        });
        // Open-source buttons on each citation card.
        root.querySelectorAll(".cite-card .cite-open-source").forEach((btn) => {
            btn.addEventListener("click", async (e) => {
                e.preventDefault();
                const card = btn.closest(".cite-card");
                if (!card) return;
                const expand = card.querySelector(".cite-card-expand");
                if (expand && expand.dataset.loaded === "1") {
                    expand.hidden = !expand.hidden;
                    btn.textContent = expand.hidden ? "Open source" : "Hide source";
                    return;
                }
                btn.textContent = "Loading…";
                btn.disabled = true;
                try {
                    const sid = card.dataset.sourceId;
                    const res = await fetch(`/admin/source/${encodeURIComponent(sid)}`);
                    const data = await res.json();
                    expand.textContent = data.content || "(empty)";
                    expand.dataset.loaded = "1";
                    expand.hidden = false;
                    btn.textContent = "Hide source";
                } catch (err) {
                    expand.textContent = "Failed to load source: " + err;
                    expand.hidden = false;
                } finally {
                    btn.disabled = false;
                }
            });
        });
    };

    // Citation hover popover (singleton, appended to body).
    let citationPopover = null;
    const ensureCitationPopover = () => {
        if (citationPopover) return citationPopover;
        citationPopover = document.createElement("div");
        citationPopover.className = "cite-popover";
        citationPopover.hidden = true;
        document.body.appendChild(citationPopover);
        return citationPopover;
    };
    const showCitationPopover = (event, citation) => {
        const pop = ensureCitationPopover();
        const head = (citation.heading_path || []).join(" › ");
        pop.innerHTML = `
            <div class="cite-pop-head">
                <span class="cite-pop-id">${escapeHTML(citation.id)}</span>
                <span class="cite-pop-source">${escapeHTML(citation.source_id)}</span>
            </div>
            ${head ? `<div class="cite-pop-heading">${escapeHTML(head)}</div>` : ""}
            <div class="cite-pop-snippet">${escapeHTML(citation.snippet || "")}</div>
        `;
        pop.hidden = false;
        const rect = event.target.getBoundingClientRect();
        const popRect = pop.getBoundingClientRect();
        let left = rect.left + window.scrollX;
        let top = rect.bottom + window.scrollY + 6;
        // Keep within viewport.
        if (left + popRect.width > window.innerWidth - 12) {
            left = window.innerWidth - popRect.width - 12;
        }
        pop.style.left = `${Math.max(8, left)}px`;
        pop.style.top = `${top}px`;
    };
    const hideCitationPopover = () => {
        if (citationPopover) citationPopover.hidden = true;
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
    const streamSSE = async (url, body, renderer) => {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
            body: JSON.stringify(body),
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

    const streamChat = (question, renderer) =>
        streamSSE("/chat/stream", { question }, renderer);

    const streamWorkflow = (slug, params, renderer) =>
        streamSSE(`/workflows/${encodeURIComponent(slug)}/stream`, { params }, renderer);

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
                    case "final": {
                        wrap.classList.remove("streaming");
                        progress.remove();
                        body.hidden = false;
                        meta.hidden = false;
                        const citations = Array.isArray(ev.citations) ? ev.citations : [];
                        let rendered = renderMarkdown(ev.answer || "(no answer)");
                        rendered = decorateCitations(rendered, citations);
                        body.innerHTML = rendered;
                        if (citations.length) {
                            const list = document.createElement("div");
                            list.className = "citations-list";
                            list.innerHTML = renderCitationCards(citations);
                            body.appendChild(list);
                            wireCitationLinks(body, citations);
                        }
                        iterBadge.textContent = `${ev.iterations} step${ev.iterations === 1 ? "" : "s"} · ${citations.length} citation${citations.length === 1 ? "" : "s"} · trace ${(ev.trace_id || traceId || "").slice(-8)}`;
                        sourcesBtn.addEventListener("click", () => openSources(ev.trace_id || traceId));
                        scrollToBottom();
                        break;
                    }
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

    /* ---- Workflows drawer ----------------------------------------------- */
    const workflowsDrawer = document.getElementById("workflows-panel");
    const workflowsBody = document.getElementById("workflows-body");
    const workflowsClose = document.getElementById("workflows-close");
    const openWorkflowsBtn = document.getElementById("open-workflows");

    const closeWorkflows = () => {
        workflowsDrawer.classList.remove("open");
        drawerScrim.classList.remove("visible");
        workflowsDrawer.setAttribute("aria-hidden", "true");
    };

    let workflowsCache = null;

    const renderParamField = (param) => {
        const id = `wf-param-${param.name}`;
        const required = param.required ? " required" : "";
        const help = param.help ? `<span class="wf-help">${escapeHTML(param.help)}</span>` : "";
        const labelHtml = `<label for="${id}" class="wf-label">${escapeHTML(param.label)}${param.required ? " *" : ""}</label>`;
        if (param.type === "choice") {
            const opts = (param.choices || []).map((c) => {
                const sel = (param.default === c) ? " selected" : "";
                return `<option value="${escapeHTML(c)}"${sel}>${escapeHTML(c)}</option>`;
            }).join("");
            return `<div class="wf-field">${labelHtml}<select id="${id}" name="${param.name}"${required}>${opts}</select>${help}</div>`;
        }
        if (param.type === "number") {
            const step = param.step != null ? ` step="${param.step}"` : "";
            const val = param.default != null ? ` value="${param.default}"` : "";
            return `<div class="wf-field">${labelHtml}<input type="number" id="${id}" name="${param.name}"${step}${val}${required}/>${help}</div>`;
        }
        const val = param.default != null ? ` value="${escapeHTML(String(param.default))}"` : "";
        return `<div class="wf-field">${labelHtml}<input type="text" id="${id}" name="${param.name}"${val}${required}/>${help}</div>`;
    };

    const renderWorkflowCard = (wf) => {
        const params = wf.parameters && wf.parameters.length
            ? wf.parameters.map(renderParamField).join("")
            : `<p class="wf-no-params">No parameters — runs as-is.</p>`;
        return `
            <form class="wf-card" data-slug="${escapeHTML(wf.slug)}">
                <h3 class="wf-title">${escapeHTML(wf.title)}</h3>
                <p class="wf-desc">${escapeHTML(wf.description)}</p>
                <div class="wf-fields">${params}</div>
                <div class="wf-actions">
                    <button type="submit" class="wf-run">Run workflow</button>
                </div>
            </form>
        `;
    };

    const openWorkflows = async () => {
        workflowsDrawer.classList.add("open");
        drawerScrim.classList.add("visible");
        workflowsDrawer.setAttribute("aria-hidden", "false");
        if (workflowsCache == null) {
            workflowsBody.innerHTML = "<p class=\"brief-rendered\">Loading…</p>";
            try {
                const res = await fetch("/workflows");
                workflowsCache = await res.json();
            } catch (err) {
                workflowsBody.innerHTML = `<p class="brief-empty">Failed to load workflows: ${escapeHTML(String(err))}</p>`;
                return;
            }
        }
        if (!Array.isArray(workflowsCache) || workflowsCache.length === 0) {
            workflowsBody.innerHTML = `<p class="brief-empty">No workflows defined.</p>`;
            return;
        }
        workflowsBody.innerHTML = workflowsCache.map(renderWorkflowCard).join("");
        workflowsBody.querySelectorAll("form.wf-card").forEach((card) => {
            card.addEventListener("submit", async (ev) => {
                ev.preventDefault();
                if (inFlight) return;
                const slug = card.dataset.slug;
                const wf = workflowsCache.find((w) => w.slug === slug);
                if (!wf) return;
                const params = {};
                (wf.parameters || []).forEach((p) => {
                    const el = card.querySelector(`[name="${p.name}"]`);
                    if (el) params[p.name] = el.value;
                });
                closeWorkflows();
                inFlight = true;
                sendBtn.disabled = true;
                appendUserMessage(`Workflow · ${wf.title}`);
                const renderer = createStreamingRenderer();
                try {
                    await streamWorkflow(slug, params, renderer);
                } catch (err) {
                    renderer.fail(err.message || String(err));
                } finally {
                    inFlight = false;
                    sendBtn.disabled = false;
                    input.focus();
                }
            });
        });
    };

    openWorkflowsBtn.addEventListener("click", openWorkflows);
    workflowsClose.addEventListener("click", closeWorkflows);

    /* ---- Admin drawer (Phase 7) ----------------------------------------- */
    const adminDrawer = document.getElementById("admin-panel");
    const adminBody = document.getElementById("admin-body");
    const adminClose = document.getElementById("admin-close");
    const openAdminBtn = document.getElementById("open-admin");
    const adminTabs = document.querySelectorAll(".admin-tab");

    let adminActiveTab = "ingest";

    const closeAdmin = () => {
        adminDrawer.classList.remove("open");
        drawerScrim.classList.remove("visible");
        adminDrawer.setAttribute("aria-hidden", "true");
    };

    const openAdmin = (tab) => {
        adminDrawer.classList.add("open");
        drawerScrim.classList.add("visible");
        adminDrawer.setAttribute("aria-hidden", "false");
        selectAdminTab(tab || adminActiveTab);
    };

    const selectAdminTab = (tab) => {
        adminActiveTab = tab;
        adminTabs.forEach((t) => t.classList.toggle("active", t.dataset.tab === tab));
        adminBody.innerHTML = "<p class=\"brief-rendered\">Loading…</p>";
        if (tab === "ingest") loadIngestTab();
        else if (tab === "health") loadHealthTab();
        else if (tab === "evals") loadEvalsTab();
    };

    adminTabs.forEach((t) => t.addEventListener("click", () => selectAdminTab(t.dataset.tab)));
    openAdminBtn.addEventListener("click", () => openAdmin());
    adminClose.addEventListener("click", closeAdmin);

    /* ---- Admin: Ingest tab --------------------------------------------- */
    const loadIngestTab = async () => {
        let data;
        try {
            const res = await fetch("/admin/sources");
            if (!res.ok) throw new Error(await res.text());
            data = await res.json();
        } catch (err) {
            adminBody.innerHTML = `<p class="brief-empty">Failed to load sources: ${escapeHTML(String(err))}</p>`;
            return;
        }
        const s = data.summary || {};
        const tiles = `
            <div class="admin-tiles">
                <div class="admin-tile"><span class="admin-tile-num">${s.total_sources || 0}</span><span class="admin-tile-lbl">total sources</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${s.indexed_sources || 0}</span><span class="admin-tile-lbl">indexed</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${s.total_chunks || 0}</span><span class="admin-tile-lbl">chunks</span></div>
            </div>
            <div class="admin-rollup">
                <div><b>By bucket:</b> ${renderKVRow(s.by_bucket)}</div>
                <div><b>By license:</b> ${renderKVRow(s.by_license)}</div>
            </div>
        `;
        const rows = (data.sources || []).map((src) => {
            const refr = (src.refrigerants || []).join(", ");
            const indexedClass = src.chunk_count > 0 ? "" : "src-not-indexed";
            const onDisk = src.on_disk ? "" : "<span class=\"src-warn\">missing</span>";
            return `
                <tr class="${indexedClass}">
                    <td><code>${escapeHTML(src.source_id)}</code> ${onDisk}</td>
                    <td>${escapeHTML(src.bucket || "")}</td>
                    <td>${escapeHTML(src.type || "")}</td>
                    <td>${escapeHTML(src.manufacturer || refr || "")}</td>
                    <td class="src-num">${src.chunk_count}</td>
                    <td class="src-when">${src.last_indexed_at ? escapeHTML(src.last_indexed_at.slice(0, 16)) : "—"}</td>
                </tr>`;
        }).join("");
        adminBody.innerHTML = `
            ${tiles}
            <table class="admin-table">
                <thead><tr>
                    <th>Source</th><th>Bucket</th><th>Type</th><th>Mfr / refrigerant</th>
                    <th class="src-num">Chunks</th><th class="src-when">Last indexed</th>
                </tr></thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    };

    const renderKVRow = (obj) => {
        if (!obj) return "—";
        return Object.entries(obj).sort().map(([k, v]) =>
            `<span class="admin-kv">${escapeHTML(k)}<span class="admin-kv-n">${v}</span></span>`
        ).join("");
    };

    /* ---- Admin: Health tab --------------------------------------------- */
    const loadHealthTab = async () => {
        let data;
        try {
            const res = await fetch("/admin/health");
            if (!res.ok) throw new Error(await res.text());
            data = await res.json();
        } catch (err) {
            adminBody.innerHTML = `<p class="brief-empty">Failed to load health: ${escapeHTML(String(err))}</p>`;
            return;
        }
        const tiles = `
            <div class="admin-tiles">
                <div class="admin-tile"><span class="admin-tile-num">${data.pages_total}</span><span class="admin-tile-lbl">wiki pages</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${data.chunks_cited}/${data.chunks_total}</span><span class="admin-tile-lbl">chunks cited</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(data.orphan_chunks || []).length}</span><span class="admin-tile-lbl">orphans</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(data.thin_pages || []).length}</span><span class="admin-tile-lbl">thin pages</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(data.dangling_links || []).length}</span><span class="admin-tile-lbl">dangling links</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(data.validation_warnings || []).length}</span><span class="admin-tile-lbl">warnings</span></div>
            </div>
            <h3 class="admin-h">Coverage by bucket</h3>
            <table class="admin-table">
                <thead><tr><th>Bucket</th><th class="src-num">Cited</th><th class="src-num">Total</th><th class="src-num">Coverage</th></tr></thead>
                <tbody>${Object.entries(data.coverage_by_bucket || {}).sort().map(([b, d]) => {
                    const pct = d.total ? Math.round((d.cited / d.total) * 100) : 0;
                    return `<tr><td>${escapeHTML(b)}</td><td class="src-num">${d.cited}</td><td class="src-num">${d.total}</td><td class="src-num">${pct}%</td></tr>`;
                }).join("")}</tbody>
            </table>
            ${renderHealthList("Thin pages", data.thin_pages, (t) =>
                `<code>${escapeHTML(t.wiki_path)}</code> — ${t.chunk_count} chunks`)}
            ${renderHealthList("Dangling wikilinks", data.dangling_links, (d) =>
                `<code>${escapeHTML(d.wiki_path)}</code> → <code>[[${escapeHTML(d.missing_target)}]]</code>`)}
            ${renderHealthList("Validation warnings", data.validation_warnings, (w) =>
                `<code>${escapeHTML(w.wiki_path)}</code>: ${escapeHTML(JSON.stringify(w.warnings))}`)}
            ${renderHealthList("Orphan chunks", (data.orphan_chunks || []).slice(0, 30).map((c) => ({c})),
                (o) => `<code>${escapeHTML(o.c)}</code>`,
                (data.orphan_chunks || []).length > 30
                    ? `Showing first 30 of ${(data.orphan_chunks || []).length}.` : null)}
        `;
        adminBody.innerHTML = tiles;
    };

    const renderHealthList = (title, items, rowFn, footer = null) => {
        if (!items || items.length === 0) return "";
        const lis = items.slice(0, 30).map((it) => `<li>${rowFn(it)}</li>`).join("");
        const more = items.length > 30 ? `<p class="admin-note">… and ${items.length - 30} more.</p>` : "";
        const foot = footer ? `<p class="admin-note">${escapeHTML(footer)}</p>` : "";
        return `<h3 class="admin-h">${title} (${items.length})</h3><ul class="admin-list">${lis}</ul>${more}${foot}`;
    };

    /* ---- Admin: Evals tab ---------------------------------------------- */
    const loadEvalsTab = async () => {
        let data;
        try {
            const res = await fetch("/admin/evals");
            data = await res.json();
        } catch (err) {
            adminBody.innerHTML = `<p class="brief-empty">Failed to load evals: ${escapeHTML(String(err))}</p>`;
            return;
        }
        if (!data.runs || data.runs.length === 0) {
            adminBody.innerHTML = `
                <p class="brief-empty">
                    No eval runs yet. Generate one with:
                    <br><br>
                    <code>python scripts/run_evals.py</code>
                    <br><br>
                    Eval harness lands in Phase 8 — once it writes JSON summaries under
                    <code>data/evals/</code>, latest metrics + per-run details will surface here.
                </p>`;
            return;
        }
        const latest = data.latest;
        const m = latest && latest.metrics ? latest.metrics : {};
        const tiles = `
            <div class="admin-tiles">
                <div class="admin-tile"><span class="admin-tile-num">${(m.recall_at_5 || 0).toFixed(2)}</span><span class="admin-tile-lbl">recall@5</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(m.recall_at_10 || 0).toFixed(2)}</span><span class="admin-tile-lbl">recall@10</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(m.mrr || 0).toFixed(2)}</span><span class="admin-tile-lbl">MRR</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(m.citation_precision || 0).toFixed(2)}</span><span class="admin-tile-lbl">cite precision</span></div>
                <div class="admin-tile"><span class="admin-tile-num">${(m.claim_coverage || 0).toFixed(2)}</span><span class="admin-tile-lbl">claim coverage</span></div>
            </div>
            <h3 class="admin-h">Past runs</h3>
            <table class="admin-table">
                <thead><tr><th>Run</th><th>recall@5</th><th>MRR</th><th>cite precision</th><th>when</th></tr></thead>
                <tbody>${data.runs.map((r) => {
                    const mm = r.metrics || {};
                    const when = new Date(r.mtime * 1000).toISOString().slice(0, 16);
                    return `<tr><td><code>${escapeHTML(r.run_id)}</code></td>
                        <td class="src-num">${(mm.recall_at_5 || 0).toFixed(2)}</td>
                        <td class="src-num">${(mm.mrr || 0).toFixed(2)}</td>
                        <td class="src-num">${(mm.citation_precision || 0).toFixed(2)}</td>
                        <td class="src-when">${when}</td></tr>`;
                }).join("")}</tbody>
            </table>
        `;
        adminBody.innerHTML = tiles;
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

    const generateBriefButtonHtml = (label) =>
        `<div class="wf-actions"><button class="wf-run" id="generate-brief-btn">${label}</button></div>`;

    const bindGenerateBriefBtn = () => {
        const btn = document.getElementById("generate-brief-btn");
        if (!btn) return;
        btn.addEventListener("click", async () => {
            btn.disabled = true;
            btn.textContent = "Generating… usually under a minute";
            try {
                const res = await fetch("/briefs/generate", { method: "POST" });
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.detail || `HTTP ${res.status}`);
                }
                renderBrief(data);
                const listRes = await fetch("/briefs");
                renderOtherBriefsList(await listRes.json());
            } catch (err) {
                briefsBody.insertAdjacentHTML(
                    "beforeend",
                    `<p class="brief-empty">Couldn't generate brief: ${escapeHTML(err.message)}</p>`
                );
                btn.disabled = false;
                btn.textContent = "Generate today's brief";
            }
        });
    };

    const renderOtherBriefsList = (briefs) => {
        if (!Array.isArray(briefs) || briefs.length <= 1) return;
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
                    <p class="brief-empty">No briefs yet.</p>
                    ${generateBriefButtonHtml("Generate today's brief")}
                `;
                bindGenerateBriefBtn();
                return;
            }
            // Show the most recent brief by default; list the rest below.
            const latest = briefs[0];
            const r = await fetch(`/briefs/${latest.date}`);
            const data = await r.json();
            renderBrief(data);
            renderOtherBriefsList(briefs);
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
        briefsBody.innerHTML = `
            ${generateBriefButtonHtml("Generate today's brief")}
            <div class="brief-rendered">${fm}${renderMarkdown(body)}</div>
        `;
        bindGenerateBriefBtn();
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
        if (workflowsDrawer.classList.contains("open")) closeWorkflows();
        if (adminDrawer.classList.contains("open")) closeAdmin();
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
