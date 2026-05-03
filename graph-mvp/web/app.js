/* Graph chat client.
 *
 * - POST /chat to invoke the agent loop
 * - GET /audit/{trace_id} for the audit drawer (lazy)
 * - Markdown rendering via marked (CDN); plain-text fallback if it failed to load
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

    /* ---- Markdown rendering ---- */
    const renderMarkdown = (text) => {
        if (typeof window.marked === "object" && typeof marked.parse === "function") {
            return marked.parse(text, { breaks: true, gfm: true });
        }
        // Fallback: escape and preserve newlines
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, "<br>");
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
        const thinkingNode = appendThinkingMessage();
        inFlight = true;
        sendBtn.disabled = true;

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question }),
            });
            thinkingNode.remove();
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                appendError(err.detail || `Request failed (${res.status})`);
                return;
            }
            const data = await res.json();
            appendAssistantMessage(data.answer, data.trace_id, data.iterations);
        } catch (err) {
            thinkingNode.remove();
            appendError(`Network error: ${err.message}`);
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

    /* ---- Message rendering ---- */
    const scrollToBottom = () => {
        conversation.scrollTop = conversation.scrollHeight;
    };

    const appendUserMessage = (text) => {
        const wrap = document.createElement("div");
        wrap.className = "msg msg-user";
        wrap.innerHTML = `
            <span class="msg-role">You</span>
            <div class="msg-body"></div>
        `;
        wrap.querySelector(".msg-body").textContent = text;
        messages.appendChild(wrap);
        scrollToBottom();
    };

    const appendThinkingMessage = () => {
        const wrap = document.createElement("div");
        wrap.className = "msg msg-thinking";
        wrap.innerHTML = `
            <span class="msg-role">Graph</span>
            <div class="msg-body">
                <span class="thinking-dots"><span></span><span></span><span></span></span>
                <span>Reading the wiki and querying your data…</span>
            </div>
        `;
        messages.appendChild(wrap);
        scrollToBottom();
        return wrap;
    };

    const appendAssistantMessage = (answer, traceId, iterations) => {
        const wrap = document.createElement("div");
        wrap.className = "msg msg-assistant";
        wrap.innerHTML = `
            <span class="msg-role">Graph</span>
            <div class="msg-body"></div>
            <div class="msg-meta">
                <button class="show-sources" type="button">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M9 18h6"></path>
                        <path d="M10 22h4"></path>
                        <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"></path>
                    </svg>
                    Show sources
                </button>
                <span class="iter-badge">${iterations} step${iterations === 1 ? "" : "s"} · trace ${traceId.slice(-8)}</span>
            </div>
        `;
        wrap.querySelector(".msg-body").innerHTML = renderMarkdown(answer);
        wrap.querySelector(".show-sources").addEventListener("click", () => openSources(traceId));
        messages.appendChild(wrap);
        scrollToBottom();
    };

    const appendError = (text) => {
        const wrap = document.createElement("div");
        wrap.className = "msg msg-error";
        wrap.innerHTML = `<span class="msg-role">Error</span><div class="msg-body"></div>`;
        wrap.querySelector(".msg-body").textContent = text;
        messages.appendChild(wrap);
        scrollToBottom();
    };

    /* ---- Sources drawer ---- */
    const closeDrawer = () => {
        drawer.classList.remove("open");
        drawerScrim.classList.remove("visible");
        drawer.setAttribute("aria-hidden", "true");
        drawerScrim.setAttribute("aria-hidden", "true");
    };

    drawerClose.addEventListener("click", closeDrawer);
    drawerScrim.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && drawer.classList.contains("open")) closeDrawer();
    });

    const openSources = async (traceId) => {
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

    const escapeHTML = (s) =>
        String(s).replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
        }[c]));

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

        // Add a small footer with trace id for copy/paste
        const footer = document.createElement("p");
        footer.style.cssText = "margin-top:24px;font-size:11px;color:var(--text-faint);font-family:var(--font-mono);";
        footer.textContent = `trace_id: ${traceId}`;
        drawerBody.appendChild(footer);
    };
})();
