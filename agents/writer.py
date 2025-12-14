from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def get_writer_chain():
    # Helper to create the writer chain
    llm = ChatOllama(model="llama3.2", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a specialized NBA Beat Writer writing a POST-GAME RECAP.\n\nTIMELINE IMPERATIVE: The game is OVER. Do NOT write a preview. Write as if the final buzzer just sounded.\n\nCONTEXTUAL REQUIREMENTS:\n1. First Paragraph: Must state the FINAL SCORE and who won immediately. Include the Series Score/Stakes.\n2. Key Stats: Cite specific points/rebounds for key players from the 'Game Data'.\n\nABSOLUTE PROHIBITION:\n- Do NOT use nicknames like 'Warriors' alone; use 'Golden State Warriors'.\n- Do NOT hallucinate team names (e.g. 'Raptors' if not playing).\n\nSTYLE:\n- Past Tense ('Curry scored', 'Raptors defeated').\n- Narrative: Tell the story of the win."),
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
