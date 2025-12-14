import pandas as pd
import os

# Define Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', '..', 'data', 'archive')
GAMES_PATH = os.path.join(DATA_DIR, 'games.csv')
DETAILS_PATH = os.path.join(DATA_DIR, 'games_details.csv')

def analyze():
    print("--- SportsEdit-AI Deep Data Integrity Check ---")
    print(f"Checking data in: {DATA_DIR}")
    
    if not os.path.exists(GAMES_PATH) or not os.path.exists(DETAILS_PATH):
        print("CRITICAL: One or more data files are missing.")
        return

    # 1. Load Data
    print("Loading games.csv...")
    df_games = pd.read_csv(GAMES_PATH, usecols=['GAME_ID', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID'], 
                           dtype={'GAME_ID': str, 'HOME_TEAM_ID': str, 'VISITOR_TEAM_ID': str}, low_memory=False)
    
    print("Loading games_details.csv...")
    df_details = pd.read_csv(DETAILS_PATH, usecols=['GAME_ID', 'TEAM_ID'], 
                             dtype={'GAME_ID': str, 'TEAM_ID': str}, low_memory=False)
    
    # 2. Logic Logic: What teams are ACTUALLY in the details?
    print("Grouping details by Game ID...")
    # Group by GAME_ID and get set of TEAM_IDs for each game
    details_teams = df_details.groupby('GAME_ID')['TEAM_ID'].apply(set).to_dict()
    
    # 3. Verify Consistency
    print("Verifying semantic consistency...")
    
    perfect_matches = 0
    partial_matches = 0
    mismatches = 0
    orphans = 0 # Games with no details
    
    perfect_matches_examples = []
    mismatch_example = None
    
    total_games = len(df_games)
    
    for _, row in df_games.iterrows():
        gid = row['GAME_ID']
        expected_teams = {row['HOME_TEAM_ID'], row['VISITOR_TEAM_ID']}
        
        if gid not in details_teams:
            orphans += 1
            continue
            
        actual_teams = details_teams[gid]
        
        # Check if actual teams match expected teams
        if expected_teams == actual_teams:
            perfect_matches += 1
            if len(perfect_matches_examples) < 5:
                # Convert sets to sorted lists for cleaner printing
                perfect_matches_examples.append({
                    "game_id": gid,
                    "expected": sorted(list(expected_teams)),
                    "actual": sorted(list(actual_teams))
                })
        elif actual_teams.issubset(expected_teams) or expected_teams.issubset(actual_teams):
            partial_matches += 1
        else:
            mismatches += 1
            if not mismatch_example:
                mismatch_example = {
                    "game_id": gid,
                    "expected": expected_teams,
                    "actual": actual_teams
                }

    # 4. Report
    print("\n--- DEEP ANALYSIS RESULTS ---")
    print(f"Total Games Analyzed: {total_games}")
    print(f"Perfect Matches (Both teams correct): {perfect_matches} ({perfect_matches/total_games*100:.2f}%)")
    print(f"Partial Matches (One team missing/extra?): {partial_matches} ({partial_matches/total_games*100:.2f}%)")
    print(f"Mismatches (Alien teams found): {mismatches} ({mismatches/total_games*100:.2f}%)")
    print(f"Orphans (No details found): {orphans} ({orphans/total_games*100:.2f}%)")
    
    print("\n--- PERFECT MATCH EXAMPLES (For Manual Verification) ---")
    # We'll just take the first 5 we found
    for i, example in enumerate(perfect_matches_examples[:5]):
        print(f"Match #{i+1}: Game ID {example['game_id']}")
        print(f"  Expected: {example['expected']}")
        print(f"  Found:    {example['actual']}")
        print("-" * 30)

    if mismatch_example:
        print("\n--- MISMATCH EXAMPLE ---")

        print(f"Game ID: {mismatch_example['game_id']}")
        print(f"Expected (from games.csv): {mismatch_example['expected']}")
        print(f"Actual (from details.csv): {mismatch_example['actual']}")
        print("Possible Cause: All-Star games? Pre-season? Trades?")
        
    print(f"\nExample Valid ID: {perfect_matches_examples[0]['game_id'] if perfect_matches_examples else 'None'}")

if __name__ == "__main__":
    analyze()
