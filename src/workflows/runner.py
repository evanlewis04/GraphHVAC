"""Workflow runner — parameter validation + prompt formatting + agent dispatch.

The public surface is two functions:

  - ``build_prompt(workflow, params)`` — validates ``params`` against the
    workflow's parameter schema and returns the formatted user message
    that goes to the agent.
  - ``run_workflow(slug, params)`` / ``stream_workflow(slug, params)``  —
    sync and SSE wrappers around the agent loop. Both inherit citations
    + audit + tool use because they go through the same loop.
"""

from __future__ import annotations

import re
from typing import Any, Iterator

from src.agent.loop import AgentResponse, run_agent, stream_agent
from src.workflows.definitions import Parameter, Workflow, get_workflow


class WorkflowError(ValueError):
    """Raised for bad workflow slug or invalid parameters."""


def _coerce(param: Parameter, raw: Any) -> Any:
    if raw is None or raw == "":
        if param.required and param.default is None:
            raise WorkflowError(f"missing required parameter: {param.name}")
        return param.default if param.default is not None else ""
    if param.type == "number":
        try:
            return float(raw) if param.step and param.step < 1 else int(float(raw))
        except (TypeError, ValueError) as exc:
            raise WorkflowError(f"parameter {param.name!r} must be a number") from exc
    if param.type == "choice":
        if str(raw) not in (param.choices or []):
            raise WorkflowError(
                f"parameter {param.name!r} must be one of {param.choices!r}"
            )
        return str(raw)
    return str(raw)


def _derived_fields(workflow: Workflow, params: dict[str, Any]) -> dict[str, Any]:
    """Compute small derived values used by some prompt templates.

    Keeps the prompt template format-string simple — caller-visible
    parameters stay clean and we synthesize the rest here.
    """
    extra: dict[str, Any] = {}
    if workflow.slug == "refrigerant-exposure":
        extra["refrigerant_slug"] = re.sub(
            r"[^a-z0-9]+", "-", str(params.get("refrigerant", "")).lower()
        ).strip("-")
    elif workflow.slug == "supplier-risk-review":
        mfr = (params.get("manufacturer") or "").strip()
        if mfr:
            extra["manufacturer_filter_clause"] = f'manufacturer = "{mfr}"'
        else:
            extra["manufacturer_filter_clause"] = "any of their equipment lines"
    elif workflow.slug == "tariff-response":
        cat = (params.get("category") or "").strip()
        if cat:
            extra["category_clause"] = f"on the {cat} line"
            extra["sql_category_clause"] = f" AND category = '{cat}'"
        else:
            extra["category_clause"] = ""
            extra["sql_category_clause"] = ""
    return extra


def build_prompt(workflow: Workflow, params: dict[str, Any]) -> str:
    """Validate parameters and return the formatted user message.

    Raises ``WorkflowError`` on validation failures.
    """
    coerced: dict[str, Any] = {}
    for p in workflow.parameters:
        coerced[p.name] = _coerce(p, params.get(p.name))
    coerced.update(_derived_fields(workflow, coerced))
    try:
        return workflow.prompt_template.format(**coerced)
    except KeyError as exc:
        raise WorkflowError(f"prompt template missing field: {exc}") from exc


def _resolve(slug: str) -> Workflow:
    workflow = get_workflow(slug)
    if workflow is None:
        raise WorkflowError(f"unknown workflow slug: {slug!r}")
    return workflow


def run_workflow(slug: str, params: dict[str, Any]) -> AgentResponse:
    workflow = _resolve(slug)
    prompt = build_prompt(workflow, params)
    return run_agent(prompt)


def stream_workflow(slug: str, params: dict[str, Any]) -> Iterator[dict[str, Any]]:
    workflow = _resolve(slug)
    prompt = build_prompt(workflow, params)
    # Tag the trace so the audit log shows which workflow ran.
    # The "started" event downstream gets workflow context attached client-side.
    yield {"kind": "workflow_started", "slug": slug, "prompt": prompt}
    yield from stream_agent(prompt)
