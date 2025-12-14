from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.writer import get_writer_chain
from agents.jury import get_fact_checker, get_style_critic, get_bias_watchdog

# Define the State
class AgentState(TypedDict):
    input_stats: str
    draft: str
    # Aggregate Jury Results
    jury_verdict: str # PASS or FAIL
    jury_feedback: List[str] 
    revision_count: int

def writer_node(state: AgentState):
    chain = get_writer_chain()
    input_text = state['input_stats']
    
    # Append feedback if retrying
    if state.get('jury_feedback') and state['revision_count'] > 0:
        feedback_str = "; ".join(state['jury_feedback'])
        input_text += f"\n\nCRITICAL FEEDBACK FROM JURY: {feedback_str}. Fix these errors."
        
    response = chain.invoke({"stats": input_text})
    return {"draft": response.content, "revision_count": state.get("revision_count", 0) + 1}

def jury_node(state: AgentState):
    # Run in "Parallel" (sequentially here for simplicity on single GPU, 
    # but logically distinct).
    
    draft = state['draft']
    stats = state['input_stats']
    
    # 1. Fact Check
    fact_agent = get_fact_checker()
    try:
        fact_res = fact_agent.invoke({"stats": stats, "draft": draft})
    except:
        fact_res = {"status": "FAIL", "errors": ["Fact check parsing error"]}

    # 2. Bias Check
    bias_agent = get_bias_watchdog()
    try:
        bias_res = bias_agent.invoke({"draft": draft})
    except:
        bias_res = {"status": "FAIL", "issues": ["Bias check parsing error"]}
        
    # 3. Style Check (Optional - doesn't block unless terrible, but let's just log it)
    style_agent = get_style_critic()
    try:
        style_res = style_agent.invoke({"draft": draft})
    except:
        style_res = {"status": "PASS", "feedback": "Style check failed"}

    # Aggregation Logic (Veto Power)
    verdict = "PASS"
    feedback = []
    
    if fact_res.get("status") == "FAIL":
        verdict = "FAIL"
        feedback.extend([f"FACT: {e}" for e in fact_res.get("errors", [])])
        
    if bias_res.get("status") == "FAIL":
        verdict = "FAIL"
        feedback.extend([f"BIAS: {i}" for i in bias_res.get("issues", [])])

    # Style feedback just for info, unless we want to enforce it. 
    # Let's enforce it if it's a FAIL.
    if style_res.get("status") == "FAIL":
        # Maybe strict=False for style? Let's be strict for now.
        # verdict = "FAIL" 
        feedback.append(f"STYLE: {style_res.get('feedback')}")

    return {
        "jury_verdict": verdict,
        "jury_feedback": feedback
    }

def should_revise(state: AgentState):
    if state['jury_verdict'] == "PASS":
        return "end"
    if state['revision_count'] >= 3:
        return "end"
    return "rewrite"

# Graph Construction
workflow = StateGraph(AgentState)
workflow.add_node("writer", writer_node)
workflow.add_node("jury", jury_node)

workflow.set_entry_point("writer")
workflow.add_edge("writer", "jury")
workflow.add_conditional_edges(
    "jury",
    should_revise,
    {
        "rewrite": "writer",
        "end": END
    }
)

app = workflow.compile()
