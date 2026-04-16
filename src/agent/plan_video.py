from __future__ import annotations

import json
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from agent.graph_state import SceneSpec, ShotPlan, State


llm = init_chat_model("openai:gpt-4.1")


class SceneSpecModel(BaseModel):
    title: str
    concept: str
    audience: str
    teaching_goal: str
    visual_style: Literal[
        "math_clean",
        "physics_diagram",
        "graph_explainer",
        "mission_walkthrough",
        "process_explainer",
        "hybrid_story",
    ]
    visual_mode: Literal["conceptual", "quantitative", "hybrid"]
    narrative_style: Literal[
        "mission_walkthrough",
        "process_explainer",
        "derivation_explainer",
        "mechanism_explainer",
        "concept_explainer",
    ]
    continuity_rules: list[str] = Field(default_factory=list)
    banned_patterns: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    layout_strategy: list[str] = Field(default_factory=list)


class ShotPlanModel(BaseModel):
    shot_id: str
    order: int
    purpose: str
    narration: str
    continuity_from_previous: str
    visible_objects: list[str] = Field(default_factory=list)
    candidate_symbols: list[str] = Field(default_factory=list)
    animation_patterns: list[str] = Field(default_factory=list)
    expected_output: str
    difficulty: Literal["low", "medium", "high"]
    grounded_claims: list[str] = Field(default_factory=list)
    simplifications: list[str] = Field(default_factory=list)


class PlannerOutput(BaseModel):
    scene_spec: SceneSpecModel
    shot_plan: list[ShotPlanModel]


SYSTEM_PROMPT = """
You are planning a single educational Manim video scene for math, science, engineering,
and real-world explainers.

Inputs:
- the user prompt,
- a route classification,
- a factual topic brief.

Your job is to turn that into:
1. one global scene specification,
2. four to eight dependent shots in order.

Hard rules:
- Build a single coherent scene, not disconnected clips.
- Each shot must build on previous shots unless it is the opening shot.
- Preserve object identity whenever possible.
- Prefer transformations over clearing and recreating everything.
- Every shot must be visually legible and teach one main idea.
- Every shot must include a short narration line in plain language.
- Use real Manim candidate symbol names when confident.
- Do not confidently invent custom Manim classes.
- For open-world grounded prompts, keep the video faithful to the supplied facts.
- If exact scale would be educationally harmful, use hybrid or conceptual mode and state
  the simplification.

Style guidance:
- math_clean: persistent axes, labels, progressive reveal
- physics_diagram: diagram first, vectors second, motion third
- graph_explainer: persistent axes, one curve focus at a time
- mission_walkthrough: phase labels, trajectory panel, craft close-up when needed
- process_explainer: pipeline or mechanism flow with persistent step labels
- hybrid_story: mix quantitative and schematic views intentionally

Candidate symbols should include both mobjects and animations when relevant, e.g.
Axes, NumberPlane, Circle, Dot, Line, Arrow, DashedLine, Arc, FunctionGraph, VGroup,
Text, DecimalNumber, ValueTracker, always_redraw, Create, FadeIn, FadeOut, Transform,
ReplacementTransform, MoveAlongPath, AnimationGroup, Succession, LaggedStart,
Circumscribe, Indicate, Flash, Rotate.

Avoid:
- abrupt full-scene resets,
- overcrowded text,
- more than two simultaneous moving focal elements,
- unsupported factual claims,
- visual clutter that makes the concept harder to follow.
""".strip()


def plan_video(state: State) -> dict:
    prompt = state.get("prompt", "")
    route_info = state.get("route_info", {})
    topic_brief = state.get("topic_brief", {})

    response = llm.with_structured_output(PlannerOutput).invoke(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                json.dumps(
                    {
                        "prompt": prompt,
                        "route_info": route_info,
                        "topic_brief": topic_brief,
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )

    scene_spec: SceneSpec = response.scene_spec.model_dump()
    shot_plan: list[ShotPlan] = [
        shot.model_dump() for shot in sorted(response.shot_plan, key=lambda item: item.order)
    ]

    shot_summary = "\n".join(
        f"{shot['order']}. {shot['purpose']}" for shot in shot_plan
    )

    return {
        "messages": [AIMessage(content=f"Planned scene:\n{shot_summary}")],
        "scene_spec": scene_spec,
        "shot_plan": shot_plan,
    }
