import pandas as pd
import os

# Relative path to data
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'archive', 'games.csv')

if not os.path.exists(DATA_PATH):
    print(f"Error: {DATA_PATH} not found.")
    exit()

try:
    df = pd.read_csv(DATA_PATH)
    df['GAME_DATE_EST'] = pd.to_datetime(df['GAME_DATE_EST'])
    
    # Filter for all Playoff Games (ID starts with '4')
    df['GAME_ID'] = df['GAME_ID'].astype(str)
    playoffs = df[df['GAME_ID'].str.startswith('4')]
    
    if playoffs.empty:
        print("No playoff games found.")
    else:
        # Sort by date descending
        playoffs = playoffs.sort_values('GAME_DATE_EST', ascending=False)
        
        # 1. Finals (June)
        finals = playoffs[playoffs['GAME_DATE_EST'].dt.month == 6]
        print("\n--- Recent Finals Games (June) ---")
        for _, row in finals.head(5).iterrows():
            print(f"Game ID: {row['GAME_ID']} | Date: {row['GAME_DATE_EST'].date()} | {row['HOME_TEAM_ID']} vs {row['VISITOR_TEAM_ID']}")
            
        # 2. General Playoffs (April/May)
        # Exclude June to show earlier rounds
        early_rounds = playoffs[playoffs['GAME_DATE_EST'].dt.month.isin([4, 5])]
        print("\n--- Recent Playoff Games (April/May) ---")
        for _, row in early_rounds.head(5).iterrows():
            print(f"Game ID: {row['GAME_ID']} | Date: {row['GAME_DATE_EST'].date()} | {row['HOME_TEAM_ID']} vs {row['VISITOR_TEAM_ID']}")

except Exception as e:
    print(f"Error: {e}")
