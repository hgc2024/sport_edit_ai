import argparse
import asyncio
import json
import os
import time
import sys

# Add project root to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import get_random_game_ids, get_game_stats
from graph import app as graph_app

async def main(args):
    print(f"Starting Batch Evaluation: {args.batch_size} games, {args.iterations} iterations per game. Type: {args.type}")
    
    game_ids = get_random_game_ids(args.batch_size, args.type)
    results = []
    
    total_start = time.time()
    
    for i, gid in enumerate(game_ids):
        print(f"[{i+1}/{len(game_ids)}] Processing Game {gid}...")
        for j in range(args.iterations):
            try:
                stats_data = get_game_stats(gid)
                if "Error" in stats_data:
                    print(f"  Skipping {gid}: Data not found")
                    continue
                
                start_t = time.time()
                inputs = {
                    "input_stats": stats_data, 
                    "draft": "", 
                    "jury_verdict": "", 
                    "jury_feedback": [], 
                    "revision_count": 0
                }
                
                # Run the graph
                final_state = await asyncio.to_thread(graph_app.invoke, inputs)
                duration = time.time() - start_t
                
                status = final_state.get("jury_verdict", "FAIL")
                revisions = final_state.get("revision_count", 0)
                
                print(f"  Iter {j+1}: {status} ({revisions} revs) in {duration:.1f}s")
                
                results.append({
                    "game_id": gid,
                    "iteration": j+1,
                    "status": status,
                    "revisions": revisions,
                    "duration": duration,
                    "errors": final_state.get("jury_feedback", [])
                })
                
            except Exception as e:
                print(f"  Error on {gid}: {e}")

    total_duration = time.time() - total_start
    
    # Summary Metrics
    total_runs = len(results)
    pass_count = len([r for r in results if r['status'] == 'PASS'])
    safety_count = len([r for r in results if r['revisions'] == 0])
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
            "throughput_arts_per_min": throughput
        },
        "results": results
    }
    
    # Save to file
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2)
        
    print("\n--- EVALUATION COMPLETE ---")
    print(f"Total Duration: {total_duration:.1f}s")
    print(f"Throughput: {throughput:.1f} articles/min")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"Safety Rate: {safety_rate:.1f}%")
    print(f"Results saved to: {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SportsEdit-AI Benchmarking Tool")
    parser.add_argument("--batch_size", type=int, default=3, help="Number of games to test")
    parser.add_argument("--iterations", type=int, default=1, help="Runs per game")
    parser.add_argument("--type", type=str, default="playoff", choices=["all", "regular", "playoff"], help="Game Type filter")
    parser.add_argument("--output", type=str, default="benchmark_results.json", help="Output JSON file path")
    
    args = parser.parse_args()
    asyncio.run(main(args))
