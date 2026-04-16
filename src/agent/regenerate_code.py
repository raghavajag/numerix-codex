from typing import Literal

from langchain.chat_models import init_chat_model
from langgraph.graph import END
from pydantic import BaseModel

from agent.graph_state import State


llm = init_chat_model("openai:gpt-4.1")


class output_code(BaseModel):
    code: str
    scene_name: str


SYSTEM_PROMPT = """
You are an expert Manim (Community Edition) debugging assistant.
Fix broken Manim code carefully using the provided runtime error, the previous code,
and any relevant context already present in the conversation.

Rules:
- Return corrected runnable Python Manim code.
- Preserve the user's intended scene and educational meaning.
- Fix only what is necessary, but feel free to refactor if needed to resolve the issue.
- Ensure the returned scene_name exactly matches the generated scene class.
- Keep compatibility with VoiceoverScene and GTTSService when they are already expected.
- Do not wrap the code in markdown fences.
""".strip()


def is_valid_code(state: State) -> Literal["correct_code", "__end__"]:
    return END if state["sandbox_error"] == "No error" else "correct_code"


def correct_code(state: State) -> dict:
    prompt = (
        "the code generated earlier has errors, see error - "
        f"{state['sandbox_error']} and the code is - {state['code']}, "
        "this is manim code, fix the error using manim docs."
    )
    response = llm.with_structured_output(output_code).invoke(
        [
            ("system", SYSTEM_PROMPT),
            *state.get("messages", []),
            ("human", prompt),
        ]
    )

    return {
        "code": response.code,
        "scene_name": response.scene_name,
    }
