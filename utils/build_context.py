import pandas as pd
import os
import json
import argparse
from tqdm import tqdm

# Path Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data', 'archive')
GAMES_PATH = os.path.join(DATA_DIR, 'games.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'context_cache')

def build_context(limit=None):
    if not os.path.exists(GAMES_PATH):
        print(f"Error: {GAMES_PATH} not found.")
        return

    print(f"Loading {GAMES_PATH}...")
    df = pd.read_csv(GAMES_PATH)
    
    # Sort chronologically to replay history
    print("Sorting games chronologically...")
    df['GAME_DATE_EST'] = pd.to_datetime(df['GAME_DATE_EST'])
    df = df.sort_values('GAME_DATE_EST')
    
    # Initialize State
    # team_stats = { TEAM_ID: { 'wins': 0, 'losses': 0, 'streak': 0, 'last_10': [] } }
    team_stats = {}
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Processing context for {len(df)} games...")
    if limit:
        print(f"Running with LIMIT={limit}")
        df = df.head(limit)
        
    count = 0
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        game_id = str(row['GAME_ID'])
        home_id = row['HOME_TEAM_ID']
        visitor_id = row['VISITOR_TEAM_ID']
        season = row['SEASON']
        
        # 1. RETRIEVE Context (Before updating stats with this game result)
        home_ctx = team_stats.get(home_id, {'wins': 0, 'losses': 0, 'streak': 0})
        vis_ctx = team_stats.get(visitor_id, {'wins': 0, 'losses': 0, 'streak': 0})
        
        # Calculate Records
        home_rec = f"{home_ctx['wins']}-{home_ctx['losses']}"
        vis_rec = f"{vis_ctx['wins']}-{vis_ctx['losses']}"
        
        # Narrative Logic
        narrative = []
        if abs(home_ctx['streak']) >= 3:
            type_str = "Winning" if home_ctx['streak'] > 0 else "Losing"
            narrative.append(f"Home Team is on a {abs(home_ctx['streak'])}-game {type_str} Streak.")
        
        snapshot = {
            "game_id": game_id,
            "date": str(row['GAME_DATE_EST'].date()),
            "season": int(season),
            "home_record": home_rec,
            "visitor_record": vis_rec,
            "home_streak": home_ctx['streak'],
            "visitor_streak": vis_ctx['streak'],
            "narrative_notes": narrative
        }
        
        # Save Snapshot
        with open(os.path.join(OUTPUT_DIR, f"{game_id}.json"), 'w') as f:
            json.dump(snapshot, f)
            
        # 2. UPDATE State (After game is played)
        # Check who won
        if pd.isna(row['PTS_home']) or pd.isna(row['PTS_away']):
             continue # Skip updating if stats missing
             
        home_win = row['PTS_home'] > row['PTS_away']
        
        # Init if new
        if home_id not in team_stats: team_stats[home_id] = {'wins': 0, 'losses': 0, 'streak': 0}
        if visitor_id not in team_stats: team_stats[visitor_id] = {'wins': 0, 'losses': 0, 'streak': 0}
        
        if home_win:
            team_stats[home_id]['wins'] += 1
            if team_stats[home_id]['streak'] > 0: team_stats[home_id]['streak'] += 1
            else: team_stats[home_id]['streak'] = 1
            
            team_stats[visitor_id]['losses'] += 1
            if team_stats[visitor_id]['streak'] < 0: team_stats[visitor_id]['streak'] -= 1
            else: team_stats[visitor_id]['streak'] = -1
        else:
            team_stats[home_id]['losses'] += 1
            if team_stats[home_id]['streak'] < 0: team_stats[home_id]['streak'] -= 1
            else: team_stats[home_id]['streak'] = -1
            
            team_stats[visitor_id]['wins'] += 1
            if team_stats[visitor_id]['streak'] > 0: team_stats[visitor_id]['streak'] += 1
            else: team_stats[visitor_id]['streak'] = 1

    print(f"Context build complete. Saved {len(df)} snapshots to {OUTPUT_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit number of games to process")
    args = parser.parse_args()
    build_context(args.limit)
