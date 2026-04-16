import json

from langchain.chat_models import init_chat_model
from pydantic import BaseModel

from agent.graph_state import State


llm = init_chat_model("openai:gpt-4.1")


class output_code(BaseModel):
    code: str
    scene_name: str


def _build_system_prompt(state: State) -> str:
    language = state.get("language", "en") or "en"
    mapped_chunks = json.dumps(state.get("mapped_chunks", []), indent=2, ensure_ascii=False)

    return f"""
You are an expert Manim (Community Edition) developer for educational content.

You will generate a complete Manim scene from user intent plus retrieval context from
the Manim source-code index.

RETRIEVED MANIM CONTEXT
Use this retrieved context directly when deciding which classes, methods, and patterns
to use:
{mapped_chunks}

OUTPUT REQUIREMENTS
- Return structured output with:
  - code: a complete Python code string
  - scene_name: the primary scene class name
- The code must be runnable Python and represent a single coherent educational scene.
- The scene class name in scene_name must exactly match the generated class name.

CORE IMPLEMENTATION RULES
- All imports must be explicit at the top of the file. Do not rely on wildcard
  assumptions beyond standard Manim import conventions you explicitly write.
- The main scene must inherit from VoiceoverScene.
- You must configure voiceover with GTTSService.
- GTTSService language must be "{language}" and tld must be "com".
- Use safe area margins of 0.5 units from screen edges.
- Maintain minimum spacing of 0.3 units between meaningful on-screen elements.
- Use modular helper functions for repeated animation sequences or scene construction.
- Add concise comments for complex spatial logic, layout calculations, or updater logic.
- Do not use any external assets, files, images, audio clips, or downloaded resources.
  Everything must be procedurally generated in code.
- Do not include an if __name__ == "__main__" block.
- Never use BLACK text color. Prefer BLUE_C, GREEN_C, GREY_A, GOLD_C, TEAL_C, WHITE,
  or other non-black safe colors when needed.
- Sync animation timing to voiceover whenever a voiceover tracker is active. Prefer
  run_time=tracker.duration for major narrated animations.
- If TeX or MathTex is necessary, configure a TexTemplate explicitly for any package
  additions you need.
- Manim plugins are allowed only if they clearly simplify the implementation and remain
  compatible with Manim Community Edition.
- Apply performance best practices: avoid unnecessary submobject counts, reuse mobjects
  when practical, avoid redundant transforms, and keep updaters efficient.
- Favor readable, maintainable code over clever code.

VOICEOVER PATTERN EXAMPLE
from manim import Circle, Create
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class GTTSExample(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService(lang="{language}", tld="com"))
        circle = Circle()
        with self.voiceover(text="Describe the circle being drawn.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)
        self.wait()

CONSTRUCT METHOD STRUCTURE
- Organize the construct method into clear stages using comments such as:
  - Stage 1: setup and layout
  - Stage 2: introduce core objects
  - Stage 3: animate the main explanation
  - Stage 4: summarize or conclude
- Helper methods may prepare objects, compute layout, or build recurring animation
  groups, but construct should still read like a stage-by-stage lesson flow.

SCENE DESIGN EXPECTATIONS
- Build an educational animation that is visually clear, well paced, and spatially
  organized.
- Respect the user's original request and the mapped chunk context.
- Prefer plain-language narration strings suitable for TTS.
- When multiple instructional steps are implied, sequence them clearly across the stage
  structure.
- Keep text readable and avoid clutter.
- Use comments sparingly but helpfully.

Return only the structured output fields. Do not wrap the code in markdown fences.
""".strip()


def generate_code(state: State) -> dict:
    system_prompt = _build_system_prompt(state)
    messages = state.get("messages", [])
    response = llm.with_structured_output(output_code).invoke(
        [
            ("system", system_prompt),
            *messages,
        ]
    )

    return {
        "code": response.code,
        "scene_name": response.scene_name,
    }
