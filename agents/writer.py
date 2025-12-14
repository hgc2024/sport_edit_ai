from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def get_writer_chain():
    # Helper to create the writer chain
    llm = ChatOllama(model="llama3.2", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a specialized NBA Beat Writer. Context matters: Use the provided SEASON CONTEXT (Record, Streak, Series Score) to frame your lead. \n\nRULES:\n1. NO made-up nicknames (e.g. do NOT call Warriors 'Raptors'). Use official team names only.\n2. Lead with the high stakes (e.g. 'In a crucial Game 5...', 'Snapping a losing streak...').\n3. Focus on the narrative arc, not just numbers.\n4. Keep it grounded but engaging."),
        ("user", "Game Data: {stats}")
    ])
    
    chain = prompt | llm
    return chain

if __name__ == "__main__":
    # Test block
    try:
        chain = get_writer_chain()
        print("Writer Agent initialized successfully.")
    except Exception as e:
        print(f"Error checking Writer Agent: {e}")
