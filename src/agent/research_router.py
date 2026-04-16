from __future__ import annotations

from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from agent.graph_state import RouteInfo, State


llm = init_chat_model("openai:gpt-5.4")


class PromptRoute(BaseModel):
    route: Literal[
        "concept_only",
        "named_real_world_event",
        "named_real_world_system",
        "equation_or_derivation",
        "reaction_or_pathway",
        "mixed",
    ]
    needs_external_grounding: bool
    named_entities: list[str] = Field(default_factory=list)
    time_sensitive: bool
    domain: Literal[
        "space",
        "physics",
        "math",
        "chemistry",
        "biology",
        "engineering",
        "general_science",
    ]
    ambiguity_notes: list[str] = Field(default_factory=list)


SYSTEM_PROMPT = """
You are routing educational animation prompts before planning and retrieval.

Your task is to classify whether the prompt can be handled from general conceptual
knowledge, or whether it needs external factual grounding because it references a
real-world named entity, process, event, system, recent topic, or time-sensitive fact.

Rules:
- Use needs_external_grounding=true for named missions, named products, named events,
  recent or latest topics, current scientific developments, real-world systems, named
  biological pathways, named reactions, or historical episodes where exact facts matter.
- Use concept_only only when the user is asking about a generic concept that can be
  explained without looking up current or named external facts.
- time_sensitive=true if the prompt includes recent/current/latest/today or references
  an entity whose status or timeline could have changed.
- named_entities should capture important proper nouns or canonical topic names.
- ambiguity_notes should mention under-specified parts of the prompt that may force a
  higher-level conceptual treatment.
""".strip()


def _get_prompt(state: State) -> str:
    prompt = state.get("prompt", "").strip()
    if prompt:
        return prompt

    for message in reversed(state.get("messages", [])):
        content = getattr(message, "content", "")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


def route_prompt_for_grounding(state: State) -> dict:
    prompt = _get_prompt(state)
    response = llm.with_structured_output(PromptRoute).invoke(
        [("system", SYSTEM_PROMPT), ("human", prompt)]
    )

    route_info: RouteInfo = response.model_dump()
    summary = (
        f"Route: {route_info['route']}; domain: {route_info['domain']}; "
        f"external grounding: {route_info['needs_external_grounding']}."
    )

    return {
        "messages": [AIMessage(content=summary)],
        "route_info": route_info,
    }
