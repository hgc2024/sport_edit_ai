import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import agents.judge...")
    from agents.judge import get_judge_chain
    print("Import successful.")
    
    print("Initializing Judge chain...")
    chain = get_judge_chain()
    print("Judge initialized.")
    
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
