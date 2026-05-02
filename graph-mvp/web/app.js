// Minimal chat client: POST /chat, render the answer, expose a
// "show sources" toggle that lazy-fetches GET /audit/{trace_id}.

const form = document.getElementById("chat-form");
const input = document.getElementById("question");
const messages = document.getElementById("messages");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    appendMessage("user", question);
    input.value = "";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });
        const data = await res.json();
        appendAnswer(data.answer, data.trace_id);
    } catch (err) {
        appendMessage("error", `Request failed: ${err.message}`);
    }
});

function appendMessage(role, text) {
    const node = document.createElement("div");
    node.className = `msg msg-${role}`;
    node.textContent = text;
    messages.appendChild(node);
    messages.scrollTop = messages.scrollHeight;
}

function appendAnswer(answer, traceId) {
    const wrap = document.createElement("div");
    wrap.className = "msg msg-assistant";

    const body = document.createElement("div");
    body.className = "msg-body";
    body.textContent = answer;
    wrap.appendChild(body);

    const toggle = document.createElement("button");
    toggle.className = "show-sources";
    toggle.textContent = "Show sources";

    const sources = document.createElement("pre");
    sources.className = "sources hidden";

    toggle.addEventListener("click", async () => {
        if (!sources.dataset.loaded) {
            const res = await fetch(`/audit/${traceId}`);
            sources.textContent = JSON.stringify(await res.json(), null, 2);
            sources.dataset.loaded = "1";
        }
        sources.classList.toggle("hidden");
    });

    wrap.appendChild(toggle);
    wrap.appendChild(sources);
    messages.appendChild(wrap);
    messages.scrollTop = messages.scrollHeight;
}
