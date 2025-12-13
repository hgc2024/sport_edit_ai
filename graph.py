from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.writer import get_writer_chain
from agents.judge import get_judge_chain

# Define the State
class AgentState(TypedDict):
    input_stats: str
    draft: str
    critique_status: str
    critique_errors: List[str]
    revision_count: int

# Nodes
def writer_node(state: AgentState):
    chain = get_writer_chain()
    # If there are errors, we might want to feed them back. 
    # For now, simplistic: just prompt with stats (or with stats + previous errors if we were advanced)
    # The prompt in writer.py is simple. Let's stick to the prompt.
    # If we want to support feedback loop, we'd need to update writer prompt dynamically.
    # For "Happy Path" first, let's just regenerate. 
    # But specification says: "Loop back... with specific feedback".
    # So I should update the writer prompt or pass feedback as "stats" context?
    # Let's verify prompt in writer.py: ("user", "Game Stats: {stats}")
    # I should modify writer to accept optional feedback.
    
    # Let's pass the input stats. 
    # If critiquing, we might append the critique to the stats or a new message.
    
    input_text = state['input_stats']
    if state.get('critique_errors') and state['revision_count'] > 0:
        feedback = "; ".join(state['critique_errors'])
        input_text += f"\n\nCorrection needed: {feedback}"
        
    response = chain.invoke({"stats": input_text})
    return {"draft": response.content, "revision_count": state.get("revision_count", 0) + 1}

def judge_node(state: AgentState):
    chain = get_judge_chain()
    result = chain.invoke({"stats": state['input_stats'], "draft": state['draft']})
    # result is a dict with status, errors, score (because using JsonOutputParser)
    return {
        "critique_status": result.get("status", "FAIL"), 
        "critique_errors": result.get("errors", []),
        "score": result.get("score", 0)
    }

# Conditional Logic
def should_revise(state: AgentState):
    if state['critique_status'] == "PASS":
        return "end"
    if state['revision_count'] >= 3: # Max retries
        return "end"
    return "rewrite"

# Graph Construction
workflow = StateGraph(AgentState)
workflow.add_node("writer", writer_node)
workflow.add_node("judge", judge_node)

workflow.set_entry_point("writer")
workflow.add_edge("writer", "judge")
workflow.add_conditional_edges(
    "judge",
    should_revise,
    {
        "rewrite": "writer",
        "end": END
    }
)

app = workflow.compile()

if __name__ == "__main__":
    # Test compilation
    print("Graph compiled successfully.")
