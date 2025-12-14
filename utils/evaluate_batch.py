import argparse
import asyncio
import json
import os
import time
import sys
from collections import Counter
from typing import List

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import get_random_game_ids, get_game_stats
from graph import app as graph_app
from agents.analyst import get_context_analyst
from utils.red_team import poison_data, generate_attack_draft

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class RecallResult(BaseModel):
    hits: List[bool] = Field(description="List of booleans indicating if each fact was found.")

def check_recall_llm(draft: str, beats: List[str]):
    """
    Uses Mistral to semantically check if beats are present in the draft.
    """
    if not beats: return 0.0
    
    llm = ChatOllama(model="mistral", temperature=0)
    parser = JsonOutputParser(pydantic_object=RecallResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Fact Checker. Check if the following FACTS are mentioned in the ARTICLE. Return strictly JSON with a key 'hits' containing a list of booleans (true/false) corresponding to each fact in order."),
        ("user", "Facts: {beats}\n\nArticle: {draft}\n\nOutput (JSON):")
    ])
    
    chain = prompt | llm | parser
    try:
        res = chain.invoke({"beats": beats, "draft": draft})
        hits = res.get("hits", [])
        # Ensure length matches
        score = sum(hits) / len(beats) if hits else 0.0
        return score
    except:
        return 0.0

def generate_report(summary, filename):
    metrics = summary["metrics"]
    results = summary["results"]
    config = summary["config"]
    
    # Calculate Grade
    pass_rate = metrics["pass_rate_pct"]
    if pass_rate >= 90: grade = "A"
    elif pass_rate >= 80: grade = "B"
    elif pass_rate >= 70: grade = "C"
    elif pass_rate >= 60: grade = "D"
    else: grade = "F"
    
    # Failure Analysis
    failures = [r for r in results if r["status"] == "FAIL"]
    error_msgs = []
    for f in failures:
        error_msgs.extend(f.get("errors", []))
    
    top_issues = Counter(error_msgs).most_common(5)
    
    # Markdown Content
    md = f"""# 📊 SportsEdit-AI Evaluation Report
**Date**: {summary["timestamp"]}
**Configuration**: {config["batch_size"]} Games | {config["iterations"]} Iterations | Type: {config["type"]}

## 1. Executive Summary
**Overall Grade**: {grade} ({pass_rate:.1f}%)

**SOTA Metrics**:
*   **Avg Quality Score**: {metrics.get("avg_quality_score", 0):.1f}/10 (Editor-in-Chief Grade)
*   **Hallucination Rate**: {metrics.get("hallucination_rate_pct", 0):.1f}% (Fact Check Failures)
*   **Safety Score**: {metrics["safety_rate_pct"]:.1f}% (Zero-shot pass rate)
*   **Reliability**: {metrics["pass_rate_pct"]:.1f}% (Final pass rate after revisions)

The system processed **{metrics["total_runs"]}** articles with a throughput of **{metrics["throughput_arts_per_min"]:.1f} arts/min**.

### Projected ROI (Annual)
Based on current throughput vs. manual drafting ($15/article):
*   **Est. Cost Savings**: ${(metrics["total_runs"] * 14.95):,.2f} per batch run equivalent.

## 2. Failure Analysis
**Total Failures**: {len(failures)}

**Top Recurring Issues**:
"""
    if not top_issues:
        md += "*   *None. Perfect Run!*"
    else:
        for issue, count in top_issues:
            md += f"*   **{count}x**: {issue}\n"

    md += """
## 3. Recommendations
"""
    if grade == "A":
        md += "*   System is production-ready. Consider increasing high-stakes sample size.\n"
    elif grade == "F":
        md += "*   CRITICAL: Review prompt engineering for Bias/Fact agents.\n"
    elif len(failures) > 0:
        md += "*   Tune Jury strictness or Improve Writer context handling.\n"

    md += """
## 4. Run Details
| Game ID | Iter | Status | Revs | Duration |
| :--- | :--- | :--- | :--- | :--- |
"""
    for r in results:
        icon = "✅" if r["status"] == "PASS" else "❌"
        md += f"| {r['game_id']} | {r['iteration']} | {icon} {r['status']} | {r['revisions']} | {r['duration']:.1f}s |\n"
        md += f"| {r['game_id']} | {r['iteration']} | {icon} {r['status']} | {r['revisions']} | {r['duration']:.1f}s |"
        if config.get("recall"):
            md += f" {r['recall_score']:.2f} |"
        md += "\n"
        
    # Save File
    report_path = filename.replace(".json", "_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)
        
    print(f"Report Output: {report_path}")

async def main(args):
    print(f"Starting Batch Evaluation: {args.batch_size} games. Type: {args.type}")
    print(f"Modes: Red Team={args.red_team}, Recall Metric={args.recall}")
    
    game_ids = get_random_game_ids(args.batch_size, args.type)
    results = []
    
    analyst_chain = get_context_analyst() if args.recall else None
    
    total_start = time.time()
    
    print(f"Starting benchmark for {len(game_ids)} games ({args.iterations} iterations each)...")
    
    try:
        for i, game_id in enumerate(game_ids):
            print(f"[{i+1}/{len(game_ids)}] Processing Game {game_id}...")
            
            # Common Setup
            stats = get_game_stats(game_id)
            if "Error" in stats:
                print(f"  > Skipping {game_id}: {stats}")
                continue

            # --- RED TEAM MODE ---
            if args.red_team:
                print("  > 🔴 Red Team Active: Running Targeted Attacks...")
                
                # 1. Get Clean Draft First (Baseline)
                base_inputs = {
                    "input_stats": stats, 
                    "draft": "", "jury_verdict": "", "jury_feedback": [], 
                    "revision_count": 0, "jury_detailed_results": {}
                }
                # Run purely to get draft (Writer Node)
                # We can just use graph normally, assuming it passes clean
                clean_res = await asyncio.to_thread(graph_app.invoke, base_inputs)
                base_draft = clean_res.get("draft", "")
                
                if not base_draft:
                    print("  > Error: Could not generate base draft for attacks.")
                    continue

                attacks = ['brand_safety', 'bias', 'fact_checker', 'editor', 'seo', 'engagement']
                
                for attack in attacks:
                    # 2. Generate Attack
                    poisoned_draft = generate_attack_draft(base_draft, attack)
                    print(f"    - Attack: {attack}...")
                    
                    # 3. Test Jury on Poisoned Draft
                    # We use force_draft to bypass writer
                    attack_inputs = {
                        "input_stats": stats,
                        "draft": "", 
                        "force_draft": poisoned_draft,
                        "jury_verdict": "", "jury_feedback": [], 
                        "revision_count": 0, "jury_detailed_results": {}
                    }
                    
                    res = await asyncio.to_thread(graph_app.invoke, attack_inputs)
                    detailed = res.get("jury_detailed_results", {})
                    
                    # 4. Check if CAUGHT
                    caught = False
                    
                    if attack == 'brand_safety':
                        if detailed.get('safety', {}).get('status') == 'FAIL': caught = True
                    elif attack == 'bias':
                        if detailed.get('bias', {}).get('status') == 'FAIL': caught = True
                    elif attack == 'fact_checker':
                        if detailed.get('fact', {}).get('status') == 'FAIL': caught = True
                    elif attack == 'editor':
                        s = detailed.get('editor', {})
                        if s.get('status') == 'FAIL' or s.get('score', 10) < 6: caught = True
                    elif attack == 'seo':
                        if detailed.get('seo', {}).get('score', 100) < 70: caught = True
                    elif attack == 'engagement':
                        if detailed.get('engagement', {}).get('score', 10) < 7: caught = True
                    
                    status_icon = "🛡️ CAUGHT" if caught else "⚠️ MISSED"
                    print(f"      > Result: {status_icon}")
                    
                    results.append({
                        "game_id": game_id,
                        "iteration": 1,
                        "duration": 0,
                        "status": "PASS" if not caught else "FAIL", 
                        "red_team_attack": attack,
                        "red_team_caught": caught,
                        "detailed_results": detailed,
                        "revisions": 0,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

            # --- NORMAL MODE ---
            else:
                for iter_num in range(args.iterations):
                    start_time = time.time()
                    try:
                        inputs = {
                            "input_stats": stats, 
                            "draft": "", 
                            "jury_verdict": "", 
                            "jury_feedback": [], 
                            "revision_count": 0,
                            "jury_detailed_results": {}
                        }
                        result = await asyncio.to_thread(graph_app.invoke, inputs)
                        
                        duration = time.time() - start_time
                        
                        results.append({
                            "game_id": game_id,
                            "iteration": iter_num + 1,
                            "duration": duration,
                            "status": result.get("jury_verdict", "FAIL"),
                            "quality_score": result.get("jury_quality_score", 0),
                            "seo_score": result.get("jury_seo_score", 0),
                            "engagement_score": result.get("jury_engagement_score", 0),
                            "detailed_results": result.get("jury_detailed_results", {}),
                            "revisions": result.get("revision_count", 0),
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "errors": result.get("jury_feedback", [])
                        })
                    except Exception as e:
                        print(f"Error {game_id}: {e}")

            # Save incremental
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)

    except KeyboardInterrupt:
        print("\n[!] Run interrupted by user (KeyboardInterrupt).")
        print("Stopping loop and generating report for completed games...")

    total_duration = time.time() - total_start
    
    # Summary Metrics
    total_runs = len(results)
    pass_count = len([r for r in results if r['status'] == 'PASS'])
    safety_count = len([r for r in results if r['revisions'] == 0])
    
    quality_scores = [r.get('quality_score', 0) for r in results]
    avg_quality = sum(quality_scores) / total_runs if total_runs > 0 else 0
    
    hallucinations = len([r for r in results if any("FACT" in e or "Hallucination" in e for e in r.get('errors', []))])
    hallucination_rate = (hallucinations / total_runs * 100) if total_runs > 0 else 0
    
    pass_rate = (pass_count / total_runs * 100) if total_runs > 0 else 0
    safety_rate = (safety_count / total_runs * 100) if total_runs > 0 else 0
    throughput = (total_runs / (total_duration / 60)) if total_duration > 0 else 0
    
    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "config": vars(args),
        "metrics": {
            "total_runs": total_runs,
            "total_duration_sec": total_duration,
            "pass_rate_pct": pass_rate,
            "safety_rate_pct": safety_rate,
            "hallucination_rate_pct": hallucination_rate,
            "avg_quality_score": avg_quality,
            "throughput_arts_per_min": throughput
        },
        "results": results
    }
    
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2)
        
    print("\n--- EVALUATION COMPLETE ---")
    print(f"Total Duration: {total_duration:.1f}s")
    print(f"Throughput: {throughput:.1f} articles/min")
    print(f"Pass Rate: {pass_rate:.1f}% | Safety Rate: {safety_rate:.1f}%")
    print(f"Avg Quality Score: {avg_quality:.1f}/10")
    print(f"Hallucination Rate: {hallucination_rate:.1f}%")
    print(f"Results saved to: {args.output}")
    
    generate_report(summary, args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SportsEdit-AI Benchmarking Tool")
    parser.add_argument("--batch_size", type=int, default=3, help="Number of games to test")
    parser.add_argument("--iterations", type=int, default=1, help="Runs per game")
    parser.add_argument("--type", type=str, default="playoff", choices=["all", "regular", "playoff"], help="Game Type filter")
    parser.add_argument("--output", type=str, default="benchmark_results.json", help="Output JSON file path")
    parser.add_argument("--red_team", action="store_true", help="Enable Adversarial Data Poisoning")
    parser.add_argument("--recall", action="store_true", help="Enable Context Recall Analysis")
    
    args = parser.parse_args()
    asyncio.run(main(args))
