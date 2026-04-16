from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from agent.analyze_user_prompt import analyze_user_prompt, animation_required
from agent.enhance_prompt import enhanced_prompt
from agent.execute_code import execute_code
from agent.generate_code import generate_code
from agent.graph_state import State
from agent.map_reduce import continue_instructions, get_chunks
from agent.regenerate_code import correct_code, is_valid_code


graph = StateGraph(State)

graph.add_node("analyze_user_prompt", analyze_user_prompt)
graph.add_node("enhanced_prompt", enhanced_prompt)
graph.add_node(
    "get_chunks",
    get_chunks,
    retry_policy=RetryPolicy(
        max_attempts=3,
        initial_interval=1.0,
        backoff_factor=2.0,
    ),
)
graph.add_node("generate_code", generate_code)
graph.add_node("correct_code", correct_code)
graph.add_node("execute_code", execute_code)

graph.add_edge(START, "analyze_user_prompt")
graph.add_conditional_edges(
    "analyze_user_prompt",
    animation_required,
    {
        "enhanced_prompt": "enhanced_prompt",
        END: END,
    },
)
graph.add_conditional_edges("enhanced_prompt", continue_instructions)
graph.add_edge("get_chunks", "generate_code")
graph.add_edge("generate_code", "execute_code")
graph.add_conditional_edges(
    "execute_code",
    is_valid_code,
    {
        END: END,
        "correct_code": "correct_code",
    },
)
graph.add_edge("correct_code", "execute_code")

memory = InMemorySaver()
workflow_app = graph.compile(checkpointer=memory)
