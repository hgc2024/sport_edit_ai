import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.evaluate_batch import generate_report

def regenerate(json_path):
    print(f"Reading {json_path}...")
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Check if it's the full summary or just results list
    if isinstance(data, list):
        print("Detected raw list (incremental save). Reconstructing metrics...")
        results = data
        
        # Infer Config
        game_ids = set(r['game_id'] for r in results)
        config = {
            "batch_size": len(game_ids),
            "iterations": 3, # Assumed based on data
            "type": "reconstructed",
            "recall": True, # Assumed based on data presence
            "red_team": True
        }
        
        # Calculate metrics (Robust)
        total_runs = len(results)
        pass_count = len([r for r in results if r.get('status', 'FAIL') == 'PASS'])
        safety_count = len([r for r in results if r.get('revisions', 1) == 0])
        pass_rate = (pass_count / total_runs * 100) if total_runs > 0 else 0
        safety_rate = (safety_count / total_runs * 100) if total_runs > 0 else 0
        
        # Estimate throughput
        duration = 0
        if total_runs > 1:
            fmt = "%Y-%m-%d %H:%M:%S"
            try:
                t_start = datetime.strptime(results[0]['timestamp'], fmt)
                t_end = datetime.strptime(results[-1]['timestamp'], fmt)
                duration = (t_end - t_start).total_seconds()
            except:
                duration = 0
        
        throughput = (total_runs / (duration / 60)) if duration > 0 else 0
        
        # Sanitize Results
        for r in results:
            if "recall_score" not in r: r["recall_score"] = 0
            if "errors" not in r: r["errors"] = []
            if "status" not in r: r["status"] = "FAIL"
            if "revisions" not in r: r["revisions"] = 1
            if "duration" not in r: r["duration"] = 0
            
        metrics = {
            "total_runs": total_runs,
            "total_duration_sec": duration,
            "throughput_arts_per_min": throughput,
            "pass_rate_pct": pass_rate,
            "safety_rate_pct": safety_rate
        }
        
        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "config": config,
            "metrics": metrics,
            "results": results
        }
    else:
        print("Detected full summary structure.")
        summary = data

    print("Generating report...")
    generate_report(summary, json_path)
    print("Done.")

if __name__ == "__main__":
    regenerate("benchmark_results.json")
