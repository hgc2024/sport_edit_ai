from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from utils.data_loader import get_game_stats
from graph import app as graph_app
import time
import uvicorn

app = FastAPI(title="SportsEdit-AI API")

# Allow CORS for React Client (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For local dev, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameRequest(BaseModel):
    game_id: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/draft")
async def draft_article(request: GameRequest):
    game_id = request.game_id
    start_time = time.time()
    
    # 1. Fetch Stats
    stats_data = get_game_stats(game_id)
    if "Error" in stats_data:
        raise HTTPException(status_code=404, detail=stats_data)
        
    # 2. Run Agents
    inputs = {
        "input_stats": stats_data, 
        "draft": "", 
        "critique_status": "", 
        "critique_errors": [], 
        "revision_count": 0
    }
    
    try:
        final_state = graph_app.invoke(inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    execution_time = time.time() - start_time
    
    # Return structured data for Frontend
    # Use feedback from jury if any
    return {
        "game_id": game_id,
        "draft": final_state.get('draft'),
        "status": final_state.get('jury_verdict'),
        "errors": final_state.get('jury_feedback', []),
        "revisions": final_state.get('revision_count', 0),
        "execution_time": execution_time,
        "stats_context": stats_data
    }

class EvalRequest(BaseModel):
    batch_size: int = 5
    iterations: int = 1
    game_type: str = 'all'

@app.post("/evaluate")
async def run_evaluation(request: EvalRequest):
    from utils.data_loader import get_random_game_ids
    import asyncio
    
    game_ids = get_random_game_ids(request.batch_size, request.game_type)
    results = []
    
    total_start = time.time()
    
    # Run sequentially to not OOM the GPU
    for gid in game_ids:
        for i in range(request.iterations):
            try:
                # Reuse draft logic but return internal stats
                stats_data = get_game_stats(gid)
                if "Error" in stats_data:
                    continue
                    
                start_t = time.time()
                inputs = {
                    "input_stats": stats_data, 
                    "draft": "", 
                    "jury_verdict": "", 
                    "jury_feedback": [], 
                    "revision_count": 0
                }
                final_state = await asyncio.to_thread(graph_app.invoke, inputs)
                duration = time.time() - start_t
                
                results.append({
                    "game_id": gid,
                    "iteration": i+1,
                    "status": final_state.get("jury_verdict", "FAIL"),
                    "revisions": final_state.get("revision_count", 0),
                    "duration": duration,
                    "cost_est": 0.05 # Placeholder $0.05
                })
            except Exception as e:
                print(f"Eval Error {gid}: {e}")
                
    total_duration = time.time() - total_start
    
    return {
        "total_duration": total_duration,
        "total_runs": len(results),
        "results": results,
        "games_processed": game_ids
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
