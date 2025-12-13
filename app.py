import streamlit as st
import time
from utils.data_loader import get_game_stats
from graph import app as graph_app
import pandas as pd
import os

# Configuration
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'archive', 'games_details.csv')
GAMES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'archive', 'games.csv')

def load_games_list():
    # Load games.csv to get matchups/dates if possible, or just scan details.
    # games_details.csv is huge. games.csv is 4MB. Use games.csv for selection.
    if os.path.exists(GAMES_PATH):
        df = pd.read_csv(GAMES_PATH)
        # Sort by date desc
        df['GAME_DATE_EST'] = pd.to_datetime(df['GAME_DATE_EST'])
        df = df.sort_values('GAME_DATE_EST', ascending=False).head(50) # Just top 50 recent
        return df[['GAME_ID', 'GAME_DATE_EST', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID']]
        # Realistically we need team names. teams.csv has names.
    return pd.DataFrame()

st.set_page_config(layout="wide", page_title="SportsEdit-AI Newsroom")

st.title("🏀 SportsEdit-AI: Agentic Newsroom")

# ROI Calculator Header
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Writer Model", "Llama 3.2 (3B)")
with col2:
    st.metric("Judge Model", "Mistral (7B)")
with col3:
    st.metric("Inference Cost", "$0.00 (Local)")

# Sidebar
st.sidebar.header("Mission Control")
game_id_input = st.sidebar.text_input("Enter Game ID manually", value="22200477")
# If we had a better selector, we'd use it. For now, manual ID or a robust selector is hard without pre-processing.

if st.sidebar.button("Draft Article"):
    with st.spinner("Agents at work..."):
        start_time = time.time()
        
        # 1. Fetch Data
        stats_data = get_game_stats(game_id_input)
        
        if "Error" in stats_data:
            st.error(stats_data)
        else:
            st.success("Data fetched successfully!")
            with st.expander("View Raw Stats Context"):
                st.code(stats_data)
            
            # 2. Run Graph
            inputs = {
                "input_stats": stats_data, 
                "draft": "", 
                "critique_status": "", 
                "critique_errors": [], 
                "revision_count": 0
            }
            
            # Streaming flow for UI updates could be nice, but invoke is simpler
            final_state = inputs
            try:
                # We iterate to capture steps if we want updates
                # For now, just invoke
                final_state = graph_app.invoke(inputs)
                
                execution_time = time.time() - start_time
                human_time = 15 * 60 # 15 mins for a human
                time_saved = human_time - execution_time
                
                # Metrics Update
                st.toast(f"Pipeline finished in {execution_time:.2f}s")
                
                # Layout
                left, right = st.columns([2, 1])
                
                with left:
                    st.header("Final Draft")
                    st.write(final_state['draft'])
                    st.info(f"Total Revisions: {final_state.get('revision_count', 0)}")

                with right:
                    st.header("Verification Log")
                    status = final_state.get('critique_status', 'UNKNOWN')
                    color = "green" if status == "PASS" else "red"
                    st.markdown(f"**Final Status:** :{color}[{status}]")
                    
                    if final_state.get('critique_errors'):
                        st.warning("Issues Found during process:")
                        for err in final_state['critique_errors']:
                            st.write(f"- {err}")
                    else:
                        st.balloons()
                        st.write("No factual errors detected in final pass.")

                # ROI Display
                st.divider()
                st.subheader("ROI Analysis (Western Digital Style)")
                r1, r2 = st.columns(2)
                r1.metric("Time Saved", f"{time_saved/60:.1f} minutes")
                r2.metric("Est. Human Cost ($60/hr)", f"${(human_time/3600)*60:.2f}")

            except Exception as e:
                st.error(f"Agent Pipeline Failed: {str(e)}")
                # Helpful debug for Local LLM issues
                st.caption("Ensure Ollama is running (`ollama serve`) and models are pulled (`ollama pull llama3.2`, `ollama pull mistral`).")
