from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Define the expected JSON output structure
class JudgeOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    errors: List[str] = Field(description="List of factual errors found (e.g. numeric mismatches)")
    score: int = Field(description="Quality score from 0 to 100")

def get_judge_chain():
    # Using Mistral for better reasoning/logic
    llm = ChatOllama(model="mistral", temperature=0.0)
    
    parser = JsonOutputParser(pydantic_object=JudgeOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict fact-checker. Compare the text Draft against the Ground Truth Stats. Check for numeric consistency (points, rebounds, assists) and player names. Return JSON format."),
        ("user", "Ground Truth Stats: {stats}\n\nDraft Article: {draft}\n\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | parser
    return chain

if __name__ == "__main__":
    try:
        chain = get_judge_chain()
        print("Judge Agent initialized successfully.")
    except Exception as e:
        print(f"Error checking Judge Agent: {e}")
