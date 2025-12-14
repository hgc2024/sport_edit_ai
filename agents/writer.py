from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def get_writer_chain():
    # Helper to create the writer chain
    llm = ChatOllama(model="llama3.2", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a specialized NBA Beat Writer. \n\nCONTEXTUAL IMPERATIVE: You MUST use the provided 'Season Context' (Record, Streak, Series Score) in the first paragraph to set the stakes.\n\nABSOLUTE PROHIBITION (HALLUCINATIONS):\n- Do NOT use nicknames (e.g. use 'Golden State Warriors', NEVER just 'Warriors').\n- Do NOT hallucinate team names (e.g. calling Warriors 'Raptors').\n- CHECK the box score headers for exact Team Names.\n\nSTYLE GUIDE:\n1. Lead with the STAKES (Elimination game? Winning streak on line?).\n2. Focus on the narrative arc, not just numbers.\n3. Keep it grounded but engaging."),
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
