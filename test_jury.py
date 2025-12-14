import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import agents.jury...")
    from agents.jury import get_seo_strategist
    print("Import successful.")
    
    print("Initializing SEO agent...")
    agent = get_seo_strategist()
    print("Agent initialized.")
    
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
