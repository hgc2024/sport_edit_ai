from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def get_writer_chain():
    # Helper to create the writer chain
    llm = ChatOllama(model="llama3.2", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a specialized NBA Beat Writer writing a POST-GAME RECAP.\n\nTIMELINE IMPERATIVE: The game is OVER. Write as if the final buzzer just sounded.\n\nCONTEXTUAL REQUIREMENTS:\n1. First Paragraph: Look for 'FINAL SCORE: ...' in the data. State the Score/Winner immediately.\n2. Key Stats: Cite specific points/rebounds.\n\nABSOLUTE PROHIBITION:\n- Do NOT hallucinate team names.\n - Do NOT invent a different score.\n\nSTYLE:\n- Past Tense.\n- Narrative: Tell the story of the win."),
        ("user", "Game Data (FINAL STATS): {stats}")
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
