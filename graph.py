from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.writer import get_writer_chain
from agents.jury import get_fact_checker, get_editor_in_chief, get_bias_watchdog, get_seo_strategist, get_engagement_editor, get_brand_safety

# Define the State
class AgentState(TypedDict):
    input_stats: str
    draft: str
    force_draft: str # Optional: For Red Teaming to bypass writer
    # Aggregate Jury Results
    jury_verdict: str # PASS or FAIL
    jury_feedback: List[str] 
    revision_count: int
    jury_quality_score: int
    jury_seo_score: int
    jury_engagement_score: int
    jury_detailed_results: dict

def writer_node(state: AgentState):
    # RED TEAM BYPASS
    if state.get("force_draft"):
        return {"draft": state['force_draft'], "revision_count": state.get("revision_count", 0) + 1}

    chain = get_writer_chain()
    input_text = state['input_stats']
    
    # Append feedback if retrying
    if state.get('jury_feedback') and state['revision_count'] > 0:
        feedback_str = "; ".join(state['jury_feedback'])
        input_text += f"\n\nCRITICAL FEEDBACK FROM JURY: {feedback_str}. Fix these errors."
        
    response = chain.invoke({"stats": input_text})
    return {"draft": response.content, "revision_count": state.get("revision_count", 0) + 1}

def jury_node(state: AgentState):
    draft = state['draft']
    stats = state['input_stats']
    
    # --- STANDARDS DIVISION (Veto Power) ---
    # 1. Fact Check
    try:
        fact_res = get_fact_checker().invoke({"stats": stats, "draft": draft})
    except:
        fact_res = {"status": "FAIL", "errors": ["Fact check parsing error"]}

    # 2. Bias Check
    try:
        bias_res = get_bias_watchdog().invoke({"draft": draft})
    except:
        bias_res = {"status": "FAIL", "issues": ["Bias check parsing error"]}
        
    # 3. Brand Safety (New)
    try:
        safety_res = get_brand_safety().invoke({"draft": draft})
    except:
        safety_res = {"status": "PASS", "flags": ["Safety check error"]} 

    # --- EDITORIAL DIVISION ---
    # 4. Editor-in-Chief
    try:
        editor_res = get_editor_in_chief().invoke({"draft": draft})
    except:
        editor_res = {"status": "PASS", "score": 5, "feedback": "Editor check failed"}

    # --- GROWTH DIVISION ---
    # 5. SEO Strategist (New)
    try:
        seo_res = get_seo_strategist().invoke({"draft": draft})
    except:
        seo_res = {"score": 50, "suggestions": ["SEO check failed"]}

    # 6. Engagement Editor (New)
    try:
        engage_res = get_engagement_editor().invoke({"draft": draft})
    except:
        engage_res = {"score": 5, "critique": "Engagement check failed"}

    # --- AGGREGATION LOGIC ---
    verdict = "PASS"
    feedback = []
    
    # Standard Vetoes
    if fact_res.get("status") == "FAIL":
        verdict = "FAIL"
        feedback.extend([f"FACT: {e}" for e in fact_res.get("errors", [])])
        
    if bias_res.get("status") == "FAIL":
        verdict = "FAIL"
        feedback.extend([f"BIAS: {i}" for i in bias_res.get("issues", [])])
        
    if safety_res.get("status") == "FAIL":
        verdict = "FAIL"
        feedback.extend([f"SAFETY: {f}" for f in safety_res.get("flags", [])])

    # Editorial Quality (Score < 6 => FAIL)
    editor_score = editor_res.get("score", 5)
    if editor_res.get("status") == "FAIL" or editor_score < 6:
        verdict = "FAIL" 
        feedback.append(f"EDITOR (Score {editor_score}/10): {editor_res.get('feedback')}")
        
    # SEO (Score < 70 => FAIL)
    seo_score = seo_res.get("score", 0)
    if seo_score < 70:
        verdict = "FAIL"
        feedback.extend([f"SEO (Score {seo_score}): {s}" for s in seo_res.get("suggestions", [])])

    # Engagement (Score < 7 => FAIL)
    engage_score = engage_res.get("score", 0)
    if engage_score < 7:
        verdict = "FAIL"
        feedback.append(f"ENGAGEMENT (Score {engage_score}): {engage_res.get('critique')}")

    return {
        "jury_verdict": verdict,
        "jury_quality_score": editor_score,
        "jury_seo_score": seo_score,
        "jury_engagement_score": engage_score,
        "jury_detailed_results": {
            "fact": fact_res,
            "bias": bias_res,
            "safety": safety_res,
            "editor": editor_res,
            "seo": seo_res,
            "engagement": engage_res
        },
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
