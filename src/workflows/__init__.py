"""Named ops-lead workflows.

A workflow is a server-side bundle of (parameter schema + prompt template +
guidance about which tools to prefer). Calling a workflow constructs a
user message from the parameters and runs it through the same agent loop
the chat UI uses, so workflows inherit streaming, audit, and citations
for free.

  - ``definitions.py`` — the four workflow definitions and their prompts.
  - ``runner.py``       — parameter validation + prompt formatting + thin
                          wrapper around ``run_agent`` / ``stream_agent``.

The API surface lives in ``src/api/workflows.py``.
"""

from src.workflows.definitions import WORKFLOWS, get_workflow
from src.workflows.runner import build_prompt, run_workflow, stream_workflow

__all__ = [
    "WORKFLOWS",
    "get_workflow",
    "build_prompt",
    "run_workflow",
    "stream_workflow",
]
