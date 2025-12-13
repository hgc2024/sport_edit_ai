import pandas as pd
import os

# Define path to the dataset relative to this file
# database is in ../../data/archive/games_details.csv
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'archive', 'games_details.csv')

def get_game_stats(game_id: str) -> str:
    """
    Reads the games_details.csv, filters for the given game_id,
    selects top 3 scorers from both teams, and returns a formatted string.
    """
    if not os.path.exists(DATA_PATH):
        return f"Error: Dataset not found at {DATA_PATH}"

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

        # Sort by Points
        top_players = team_df.sort_values(by='PTS', ascending=False).head(3)

        team_summary = f"{team}:"
        player_summaries = []
        for _, row in top_players.iterrows():
            p_name = row.get('PLAYER_NAME', 'Unknown')
            pts = int(row.get('PTS', 0))
            reb = int(row.get('REB', 0))
            ast = int(row.get('AST', 0))
            player_summaries.append(f"{p_name} ({pts} pts, {reb} reb, {ast} ast)")
        
        team_summary += " " + ", ".join(player_summaries)
        summary_parts.append(team_summary)

    final_text = " | ".join(summary_parts)
    return final_text

if __name__ == "__main__":
    # Test with a sample Game ID from the dataset
    # We need a valid game ID. I'll pick one if I can see the file, but I can't.
    # I'll try to find one by loading the head of the file in the test block, 
    # or just ask the user to provide one if valid.
    # Actually, I can just scan the file for the first game_id.
    
    print("Testing data_loader...")
    if os.path.exists(DATA_PATH):
        try:
            # Just read a chunk to get a game_id
            df_sample = pd.read_csv(DATA_PATH, nrows=100)
            sample_id = df_sample['GAME_ID'].iloc[0]
            print(f"Found sample Game ID: {sample_id}")
            result = get_game_stats(sample_id)
            print("Output:")
            print(result)
        except Exception as e:
            print(e)
    else:
        print(f"File not found: {DATA_PATH}")
