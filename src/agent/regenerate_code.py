from __future__ import annotations

import json
from typing import Literal

from langchain.chat_models import init_chat_model
from langgraph.graph import END
from pydantic import BaseModel

from agent.graph_state import State
from rag.retriever import format_evidence_block, format_foundation_block, get_foundation_chunks


llm = init_chat_model("openai:gpt-4.1")


class CodeOutput(BaseModel):
    code: str
    scene_name: str


SYSTEM_PROMPT = """
You are fixing broken Manim Community Edition code for an educational animation.

Use:
- the runtime error,
- the previous code,
- the scene outline,
- and the retrieved evidence.

Rules:
- Preserve the intended lesson and scene flow.
- Fix only what is required, but refactor if the structure is the cause of the failure.
- Keep VoiceoverScene + GTTSService.
- Return structured output with code and scene_name only.
- Do not wrap the code in markdown fences.
""".strip()


def is_valid_code(state: State) -> Literal["correct_code", "__end__"]:
    return END if state.get("sandbox_error") == "No error" else "correct_code"


def correct_code(state: State) -> dict:
    evidence_blocks = [format_evidence_block(item) for item in state.get("retrieval_evidence", [])]
    foundation_block = format_foundation_block(get_foundation_chunks())
    response = llm.with_structured_output(CodeOutput).invoke(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                json.dumps(
                    {
                        "runtime_error": state.get("sandbox_error", ""),
                        "failed_code": state.get("code", ""),
                        "scene_name": state.get("scene_name", ""),
                        "scene_spec": state.get("scene_spec", {}),
                        "code_outline": state.get("code_outline", {}),
                        "foundation_block": foundation_block,
                        "evidence_blocks": evidence_blocks,
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )

    return {
        "code": response.code,
        "scene_name": response.scene_name,
    }
