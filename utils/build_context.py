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
    # history_archive = { season: { team_id: { 'reg_w': 0, ... } } }
    history_archive = {}
    
    # current_stats = { team_id: { 'reg_w': 0, 'reg_l': 0, 'post_w': 0, 'post_l': 0, 'streak': 0 } }
    current_stats = {}
    
    # playoff_series = { (teamA, teamB): { teamA: wins, teamB: wins } }  (Keyed by sorted tuple of IDs)
    playoff_series = {}
    
    current_season = None
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Processing context for {len(df)} games...")
    if limit:
        print(f"Running with LIMIT={limit}")
        df = df.head(limit)
        
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        game_id = str(row['GAME_ID'])
        home_id = row['HOME_TEAM_ID']
        visitor_id = row['VISITOR_TEAM_ID']
        season = row['SEASON']
        
        # --- SEASON TRANSITION ---
        if current_season is not None and season != current_season:
            history_archive[current_season] = {k: v.copy() for k, v in current_stats.items()}
            current_stats = {}
            playoff_series = {} # Reset playoff history for new season
            
        current_season = season
        
        # --- ENSURE TEAM INIT ---
        for tid in [home_id, visitor_id]:
            if tid not in current_stats:
                current_stats[tid] = {'reg_w': 0, 'reg_l': 0, 'post_w': 0, 'post_l': 0, 'streak': 0}

        # --- DETERMINE GAME TYPE ---
        if game_id.startswith('1'): continue # Skip Preseason
        is_playoff = game_id.startswith('4')
        
        # --- 1. RETRIEVE CONTEXT ---
        h_stats = current_stats[home_id]
        v_stats = current_stats[visitor_id]
        
        # Current Records
        h_reg_rec = f"{h_stats['reg_w']}-{h_stats['reg_l']}"
        v_reg_rec = f"{v_stats['reg_w']}-{v_stats['reg_l']}"
        h_post_rec = f"{h_stats['post_w']}-{h_stats['post_l']}"
        v_post_rec = f"{v_stats['post_w']}-{v_stats['post_l']}"
        
        # Historical Context
        prev_season = season - 1
        history_narrative = []
        if prev_season in history_archive:
            prev_data = history_archive[prev_season]
            def get_hist_str(tid):
                if tid in prev_data:
                    p = prev_data[tid]
                    return f"{p['reg_w']}-{p['reg_l']} (Reg), {p['post_w']}-{p['post_l']} (Post)"
                return "N/A"
            history_narrative.append(f"Last Season ({prev_season}): Home {get_hist_str(home_id)} | Visitor {get_hist_str(visitor_id)}")

        # Construct Context Narrative
        narrative = history_narrative + []
        stakes_note = ""
        series_context = ""
        
        if is_playoff:
            # Parse Playoff Info
            # ID Format: 4 + YY + 00 + R + GG?  Example: 41800406
            try:
                round_num = int(game_id[4:6]) # Index 4 (0) and 5 (4) -> 04? No, index 5.
                # Actually, standard is 4YYRRRGG. Index 5 is usually proper round. 
                # Let's trust int(game_id[-3]) as round and int(game_id[-2:]) as game.
                # Wait, 406 is game 6 of round 4? Yes. 406.
                # If ID is 8 digits: 0 1 2 3 4 5 6 7
                # 4 1 8 0 0 4 0 6
                # Round is digit 5 (and maybe 4?).
                round_char = game_id[5] # '4'
                round_val = int(round_char)
                game_num = int(game_id[-2:])
                
                round_map = {1: "First Round", 2: "Conf. Semis", 3: "Conf. Finals", 4: "NBA Finals"}
                round_name = round_map.get(round_val, f"Round {round_val}")
                
                # Series Logic
                series_key = tuple(sorted([home_id, visitor_id]))
                if game_num == 1 or series_key not in playoff_series:
                    playoff_series[series_key] = {home_id: 0, visitor_id: 0}
                    
                s_wins = playoff_series[series_key]
                h_sw = s_wins[home_id]
                v_sw = s_wins[visitor_id]
                
                # Series Status String
                if h_sw == v_sw: series_status = f"Series Tied {h_sw}-{v_sw}"
                elif h_sw > v_sw: series_status = f"Home Leads {h_sw}-{v_sw}"
                else: series_status = f"Visitor Leads {v_sw}-{h_sw}"
                
                series_context = f"{round_name} Game {game_num}: {series_status}"
                narrative.append(series_context)
                
                # Stakes
                potential_winner = None
                if h_sw == 3: potential_winner = "Home"
                if v_sw == 3: potential_winner = "Visitor"
                
                if potential_winner:
                    if round_val == 4:
                        stakes_note = f"CHAMPIONSHIP CLINCHING OPPORTUNITY for {potential_winner} Team."
                    else:
                        stakes_note = f"ELIMINATION GAME. {potential_winner} can advance."
                    narrative.append(f"*** STAKES: {stakes_note} ***")
                    
            except Exception as e:
                print(f"Error parsing playoff ID {game_id}: {e}")
        
        else:
            narrative.append(f"Regular Season: Home ({h_reg_rec}) vs Visitor ({v_reg_rec})")
            
        snapshot = {
            "game_id": game_id,
            "date": str(row['GAME_DATE_EST'].date()),
            "season": int(season),
            "is_playoff": is_playoff,
            "home_record": {
                "regular": h_reg_rec,
                "playoff": h_post_rec,
                "streak": h_stats['streak']
            },
            "visitor_record": {
                "regular": v_reg_rec,
                "playoff": v_post_rec,
                "streak": v_stats['streak']
            },
            "series_context": series_context,
            "stakes": stakes_note,
            "narrative_notes": narrative
        }
        
        with open(os.path.join(OUTPUT_DIR, f"{game_id}.json"), 'w') as f:
            json.dump(snapshot, f)
            
        # --- 2. UPDATE STATS ---
        if pd.isna(row['PTS_home']) or pd.isna(row['PTS_away']): continue 
        home_win = row['PTS_home'] > row['PTS_away']
        
        if home_win:
            if is_playoff:
                current_stats[home_id]['post_w'] += 1
                current_stats[visitor_id]['post_l'] += 1
                if series_key in playoff_series: playoff_series[series_key][home_id] += 1
            else:
                current_stats[home_id]['reg_w'] += 1
                current_stats[visitor_id]['reg_l'] += 1
                
            if current_stats[home_id]['streak'] > 0: current_stats[home_id]['streak'] += 1
            else: current_stats[home_id]['streak'] = 1
            if current_stats[visitor_id]['streak'] < 0: current_stats[visitor_id]['streak'] -= 1
            else: current_stats[visitor_id]['streak'] = -1
        else:
            if is_playoff:
                current_stats[home_id]['post_l'] += 1
                current_stats[visitor_id]['post_w'] += 1
                if series_key in playoff_series: playoff_series[series_key][visitor_id] += 1
            else:
                current_stats[home_id]['reg_l'] += 1
                current_stats[visitor_id]['reg_w'] += 1

            if current_stats[home_id]['streak'] < 0: current_stats[home_id]['streak'] -= 1
            else: current_stats[home_id]['streak'] = -1
            if current_stats[visitor_id]['streak'] > 0: current_stats[visitor_id]['streak'] += 1
            else: current_stats[visitor_id]['streak'] = 1

    print(f"Context build complete. Saved {len(df)} snapshots to {OUTPUT_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit number of games to process")
    args = parser.parse_args()
    build_context(args.limit)
