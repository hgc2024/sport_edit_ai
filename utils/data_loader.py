import json
import pandas as pd
import os

# Define path to the dataset relative to this file
# database is in ../../data/archive/games_details.csv
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'archive', 'games_details.csv')
CONTEXT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'context_cache')

def get_game_stats(game_id: str) -> str:
    """
    Reads the games_details.csv, filters for the given game_id,
    selects top 3 scorers from both teams, and returns a formatted string.
    Augments with Context (Series/Season Record) if available.
    """
    if not os.path.exists(DATA_PATH):
        return f"Error: Dataset not found at {DATA_PATH}"

    # 1. Load Deep Context (RAG)
    context_str = ""
    ctx_path = os.path.join(CONTEXT_DIR, f"{game_id}.json")
    if os.path.exists(ctx_path):
        try:
            with open(ctx_path, 'r') as f:
                ctx = json.load(f)
            
            # Parse Records (Handle Dict vs Legacy String)
            h_rec = ctx.get('home_record', {})
            v_rec = ctx.get('visitor_record', {})
            
            if isinstance(h_rec, dict):
                h_fmt = f"{h_rec.get('regular','?')} (Reg), {h_rec.get('playoff','?') if ctx.get('is_playoff') else 'N/A'} (Post)"
                v_fmt = f"{v_rec.get('regular','?')} (Reg), {v_rec.get('playoff','?') if ctx.get('is_playoff') else 'N/A'} (Post)"
                h_streak = h_rec.get('streak', 'N/A')
                v_streak = v_rec.get('streak', 'N/A')
            else:
                h_fmt = str(h_rec)
                v_fmt = str(v_rec)
                h_streak = ctx.get('home_streak', 'N/A')
                v_streak = ctx.get('visitor_streak', 'N/A')
            
            # Format Advanced Context
            lines = [f"SEASON CONTEXT ({ctx.get('season','?')}):"]
            if ctx.get('series_context'): lines.append(ctx['series_context'])
            if ctx.get('stakes'): lines.append(f"*** {ctx['stakes']} ***")
            
            lines.append(f"Home Record: {h_fmt} (Streak: {h_streak})")
            lines.append(f"Visitor Record: {v_fmt} (Streak: {v_streak})")
            lines.append(f"Narrative Notes: {'; '.join(ctx.get('narrative_notes', []))}")
            
            context_str = "\n".join(lines) + "\n"
        except Exception as e:
            print(f"Error loading context: {e}")

    try:
        df = pd.read_csv(DATA_PATH, low_memory=False)
    except Exception as e:
        return f"Error loading CSV: {str(e)}"

    # Filter by Game ID
    # Ensure game_id is handled as correct type (int vs str in CSV)
    # The CSV usually has GAME_ID as int or string. Let's force string comparison or conversion.
    df['GAME_ID'] = df['GAME_ID'].astype(str)
    game_df = df[df['GAME_ID'] == str(game_id)]

    if game_df.empty:
        return f"No records found for Game ID: {game_id}"

    # We need to identify the two teams.
    unique_teams = game_df['TEAM_ABBREVIATION'].unique()
    # Remove NaNs if any
    unique_teams = [t for t in unique_teams if isinstance(t, str)]
    
    if len(unique_teams) < 2:
        return f"Error: Could not identify two teams for Game ID {game_id}. Found: {unique_teams}"

    # Container for the summary
    summary_parts = []

    for team in unique_teams[:2]: # Take first two teams found
        team_df = game_df[game_df['TEAM_ABBREVIATION'] == team].copy()
        
        # Fill NaNs for stats
        team_df['PTS'] = team_df['PTS'].fillna(0)
        team_df['REB'] = team_df['REB'].fillna(0)
        team_df['AST'] = team_df['AST'].fillna(0)

        # Calculate Total Score
        total_score = int(team_df['PTS'].sum())

        # Sort by Points for player highlights
        top_players = team_df.sort_values(by='PTS', ascending=False).head(3)

        team_summary = f"{team} ({total_score} pts):"
        player_summaries = []
        for _, row in top_players.iterrows():
            p_name = row.get('PLAYER_NAME', 'Unknown')
            pts = int(row.get('PTS', 0))
            reb = int(row.get('REB', 0))
            ast = int(row.get('AST', 0))
            player_summaries.append(f"{p_name} ({pts} pts, {reb} reb, {ast} ast)")
        
        team_summary += " " + ", ".join(player_summaries)
        summary_parts.append({"team": team, "score": total_score, "text": team_summary})

    # Sort parts by score to implicitly show winner or just join them
    # Better: Explicitly state the final result string
    stats_text = "FINAL SCORE: "
    if len(summary_parts) == 2:
        t1 = summary_parts[0]
        t2 = summary_parts[1]
        if t1['score'] > t2['score']:
            stats_text += f"{t1['team']} ({t1['score']}) def. {t2['team']} ({t2['score']})"
        else:
            stats_text += f"{t2['team']} ({t2['score']}) def. {t1['team']} ({t1['score']})"
    
    stats_text += "\n\nDETAILS: " + " | ".join([p['text'] for p in summary_parts])


    
    # Combined Output
    if context_str:
        return f"{context_str}\nGAME STATS:\n{stats_text}"
    else:
        return stats_text

def get_random_game_ids(n: int = 5, game_type: str = 'all') -> list[str]:
    """
    Returns a list of random Game IDs.
    game_type: 'all', 'regular' (starts with 2), 'playoff' (starts with 4)
    """
    if not os.path.exists(DATA_PATH):
        return []
        
    try:
        # We read just the GAME_ID column to be fast
        df = pd.read_csv(DATA_PATH, usecols=['GAME_ID'], low_memory=False)
        df['GAME_ID'] = df['GAME_ID'].astype(str)
        
        if game_type == 'regular':
            df = df[df['GAME_ID'].str.startswith('2')]
        elif game_type == 'playoff':
            df = df[df['GAME_ID'].str.startswith('4')]
            
        unique_ids = df['GAME_ID'].unique()
        
        if len(unique_ids) < n:
            return list(unique_ids)
            
        import random
        return random.sample(list(unique_ids), n)
    except Exception as e:
        print(f"Error sampling games: {e}")
        return []

if __name__ == "__main__":
    # Test block
    if os.path.exists(DATA_PATH):
        print("Testing random batch:")
        ids = get_random_game_ids(3)
        print(f"IDs: {ids}")

