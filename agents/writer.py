from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def get_writer_chain():
    # Helper to create the writer chain
    llm = ChatOllama(model="llama3.2", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a high-energy sports journalist. Write a concise, exciting 200-word recap of the NBA game based ONLY on the provided stats. Focus on the key players' performances."),
        ("user", "Game Stats: {stats}")
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
