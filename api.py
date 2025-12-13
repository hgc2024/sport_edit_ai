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
    return {
        "game_id": game_id,
        "draft": final_state.get('draft'),
        "status": final_state.get('critique_status'),
        "errors": final_state.get('critique_errors', []),
        "revisions": final_state.get('revision_count', 0),
        "execution_time": execution_time,
        "stats_context": stats_data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
