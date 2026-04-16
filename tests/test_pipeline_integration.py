from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agent import analyze_user_prompt as analyze_module
from agent import execute_code as execute_module
from agent import generate_code as generate_module
from agent import plan_video as planner_module
from agent import research_router as router_module
from agent import research_topic as research_module
from agent.map_reduce import get_chunks
import rag.retriever as retriever_module


class _FakeStructuredInvoker:
    def __init__(self, response):
        self._response = response

    def invoke(self, _messages):
        return self._response


class _FakeLLM:
    def __init__(self, response_map: dict[type, object]):
        self._response_map = response_map

    def with_structured_output(self, schema):
        return _FakeStructuredInvoker(self._response_map[schema])


class _FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, str]:
        return {"video_url": "file:///tmp/artemis.mp4"}


def test_advanced_prompt_pipeline_runs_through_artemis_path(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in ("CHROMA_API_KEY", "CHROMA_TENANT", "CHROMA_DATABASE"):
        monkeypatch.delenv(env_name, raising=False)
    monkeypatch.setattr(retriever_module, "_maybe_dense_search", lambda *args, **kwargs: [])

    prompt = (
        "I want to understand and visualize how the recent Artemis II moon voyage was done, "
        "like from earth to moon the trajectory, the ship voyage etc!"
    )
    state = {"prompt": prompt, "language": "en", "messages": []}

    monkeypatch.setattr(
        analyze_module,
        "llm",
        _FakeLLM(
            {
                analyze_module.output_format: analyze_module.output_format(
                    animation=True,
                    non_animation_reply=None,
                )
            }
        ),
    )
    state.update(analyze_module.analyze_user_prompt(state))
    assert state["animation"] is True

    monkeypatch.setattr(
        router_module,
        "llm",
        _FakeLLM(
            {
                router_module.PromptRoute: router_module.PromptRoute(
                    route="named_real_world_event",
                    needs_external_grounding=True,
                    named_entities=["Artemis II", "Moon", "Earth"],
                    time_sensitive=True,
                    domain="space",
                    ambiguity_notes=["User asks for a teaching visualization, so the trajectory can be schematic."],
                )
            }
        ),
    )
    state.update(router_module.route_prompt_for_grounding(state))
    assert state["route_info"]["domain"] == "space"
    assert state["route_info"]["needs_external_grounding"] is True

    monkeypatch.setattr(
        research_module,
        "_collect_web_evidence",
        lambda _prompt, _route: (
            ["Artemis II mission profile free-return trajectory"],
            [
                "URL: https://www.nasa.gov/artemis-ii\nTitle: Artemis II\nSnippet: Artemis II uses a free-return trajectory after translunar injection."
            ],
        ),
    )
    monkeypatch.setattr(
        research_module,
        "llm",
        _FakeLLM(
            {
                research_module.TopicBriefModel: research_module.TopicBriefModel(
                    topic_title="Artemis II",
                    factual_summary="Artemis II is a crewed lunar flyby mission that leaves Earth orbit, performs translunar injection, flies a free-return path around the Moon, and returns to Earth.",
                    key_facts=[
                        "Artemis II is a crewed lunar flyby mission.",
                        "The mission uses a free-return trajectory around the Moon.",
                        "A schematic explainer should show the spacecraft leaving Earth orbit and curving around the Moon before returning.",
                    ],
                    quantitative_data=[],
                    process_steps=[
                        "Show Earth parking orbits.",
                        "Show translunar injection and outbound leg.",
                        "Show the lunar flyby and free-return path.",
                        "Show the return toward Earth.",
                    ],
                    visual_elements=["Earth", "Moon", "spacecraft", "trajectory path", "phase labels"],
                    spatial_relationships=["Earth and Moon should remain spatial anchors while the spacecraft moves between them."],
                    misconceptions_to_avoid=["Do not show Artemis II landing on the Moon."],
                    narration_outline=[
                        "Start in Earth orbit.",
                        "Explain the translunar injection burn.",
                        "Show the free-return loop around the Moon.",
                        "Explain the return to Earth.",
                    ],
                    recommended_visual_mode="hybrid",
                    source_registry=["https://www.nasa.gov/artemis-ii"],
                    source_snippets=["NASA describes Artemis II as a crewed lunar flyby on a free-return trajectory."],
                    unresolved_questions=[],
                )
            }
        ),
    )
    state.update(research_module.build_topic_brief(state))
    assert state["topic_brief"]["topic_title"] == "Artemis II"

    monkeypatch.setattr(
        planner_module,
        "llm",
        _FakeLLM(
            {
                planner_module.PlannerOutput: planner_module.PlannerOutput(
                    scene_spec=planner_module.SceneSpecModel(
                        title="Artemis II Mission Walkthrough",
                        concept="Artemis II trajectory",
                        audience="general science learners",
                        teaching_goal="Explain the outbound, flyby, and return phases without implying a landing.",
                        visual_style="mission_walkthrough",
                        visual_mode="hybrid",
                        narrative_style="mission_walkthrough",
                        continuity_rules=["Keep Earth and Moon visible as anchors.", "Reuse the same spacecraft dot and path."],
                        banned_patterns=["Do not show a lunar landing."],
                        success_criteria=["Trajectory path is clear.", "Phases are labeled."],
                        layout_strategy=["Use a not-to-scale Earth-Moon diagram with labels."],
                    ),
                    shot_plan=[
                        planner_module.ShotPlanModel(
                            shot_id="shot_1",
                            order=1,
                            purpose="Establish the Earth-Moon layout and label the mission phases.",
                            narration="We begin with Earth, the Moon, and the planned mission path.",
                            continuity_from_previous="Opening shot.",
                            visible_objects=["Earth", "Moon", "phase labels", "spacecraft"],
                            candidate_symbols=["Circle", "Dot", "Text", "Create", "LaggedStart"],
                            animation_patterns=["Create", "LaggedStart"],
                            expected_output="A clear opening layout with stable anchors.",
                            difficulty="medium",
                            grounded_claims=["Artemis II is a lunar flyby mission."],
                            simplifications=["Not to scale."],
                        ),
                        planner_module.ShotPlanModel(
                            shot_id="shot_2",
                            order=2,
                            purpose="Animate translunar injection and the free-return trajectory around the Moon.",
                            narration="After leaving Earth orbit, the spacecraft follows a free-return path around the Moon.",
                            continuity_from_previous="Reuse the opening Earth-Moon layout and animate the same spacecraft dot.",
                            visible_objects=["Earth", "Moon", "spacecraft", "trajectory"],
                            candidate_symbols=["Dot", "Arc", "TracedPath", "Create", "MoveAlongPath", "Text"],
                            animation_patterns=["Create", "MoveAlongPath", "Transform"],
                            expected_output="A readable schematic path from Earth to Moon and back.",
                            difficulty="high",
                            grounded_claims=[
                                "The mission uses a free-return trajectory.",
                                "The spacecraft loops around the Moon and returns to Earth.",
                            ],
                            simplifications=["Not to scale.", "Trajectory shown schematically."],
                        ),
                    ],
                )
            }
        ),
    )
    state.update(planner_module.plan_video(state))
    assert len(state["shot_plan"]) == 2

    retrieval_evidence = []
    for shot in state["shot_plan"]:
        retrieval_evidence.extend(
            get_chunks(
                {
                    "shot": shot,
                    "scene_spec": state["scene_spec"],
                    "topic_brief": state["topic_brief"],
                    "prompt": state["prompt"],
                }
            )["retrieval_evidence"]
        )
    state["retrieval_evidence"] = retrieval_evidence
    retrieved_symbols = {
        symbol
        for evidence in retrieval_evidence
        for symbol in evidence["allowed_symbols"]
    }
    assert {"Create", "MoveAlongPath", "TracedPath"} <= retrieved_symbols
    assert {"Text", "MarkupText"} & retrieved_symbols

    generated_code = (
        "from manim import *\n"
        "from manim_voiceover import VoiceoverScene\n"
        "from manim_voiceover.services.gtts import GTTSService\n\n"
        "class ArtemisMissionScene(VoiceoverScene):\n"
        "    def construct(self):\n"
        "        self.set_speech_service(GTTSService(lang=\"en\", tld=\"com\"))\n"
        "        earth = Circle(radius=0.6, color=BLUE).shift(LEFT * 3)\n"
        "        moon = Circle(radius=0.25, color=GREY_B).shift(RIGHT * 3)\n"
        "        ship = Dot(color=YELLOW).move_to(earth.get_right())\n"
        "        path = Arc(radius=3.2, angle=PI, arc_center=ORIGIN)\n"
        "        title = Text(\"Artemis II Free-Return Trajectory\").scale(0.5).to_edge(UP)\n"
        "        trail = TracedPath(ship.get_center, stroke_color=YELLOW)\n"
        "        self.add(trail)\n"
        "        self.add(title)\n"
        "        self.play(Create(earth), Create(moon), FadeIn(ship))\n"
        "        with self.voiceover(text=\"Artemis II leaves Earth orbit and follows a free-return path around the Moon.\") as tracker:\n"
        "            self.play(MoveAlongPath(ship, path), run_time=tracker.duration)\n"
        "        self.wait()\n"
    )
    monkeypatch.setattr(
        generate_module,
        "llm",
        _FakeLLM(
            {
                generate_module.OutlineOutput: generate_module.OutlineOutput(
                    scene_name="ArtemisMissionScene",
                    scene_class="ArtemisMissionScene",
                    imports=[
                        "from manim import *",
                        "from manim_voiceover import VoiceoverScene",
                        "from manim_voiceover.services.gtts import GTTSService",
                    ],
                    persistent_objects=["earth", "moon", "ship", "path", "title", "trail"],
                    helper_functions=[],
                    shot_functions=[],
                    transition_rules=["Reuse the same Earth, Moon, and ship objects."],
                    validation_checks=["VoiceoverScene is configured with GTTSService."],
                ),
                generate_module.CodeOutput: generate_module.CodeOutput(
                    code=generated_code,
                    scene_name="ArtemisMissionScene",
                ),
            }
        ),
    )
    state.update(generate_module.generate_code_outline(state))
    state.update(generate_module.generate_code(state))
    assert "VoiceoverScene" in state["code"]
    assert "GTTSService" in state["code"]
    assert "MoveAlongPath" in state["code"]

    monkeypatch.setattr(execute_module.requests, "post", lambda *args, **kwargs: _FakeResponse())
    state.update(execute_module.execute_code(state))
    assert state["sandbox_error"] == "No error"
    assert state["video_url"] == "file:///tmp/artemis.mp4"
