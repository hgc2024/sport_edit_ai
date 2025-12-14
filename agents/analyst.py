from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Define the output structure
class NarrativeBeats(BaseModel):
    beats: List[str] = Field(description="List of 3-5 key narrative beats or facts from the game.")

def get_context_analyst():
    """
    Returns a chain that identifies the 'Gold Standard' narrative beats from game stats.
    """
    llm = ChatOllama(model="llama3.2", temperature=0.1)
    
    parser = JsonOutputParser(pydantic_object=NarrativeBeats)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Sports Analyst. Your job is to identify 5-8 distinct 'story beats' from a game's box score. Ensure you cover the winner, key player performances, and any significant stats. Return strictly JSON with a single key 'beats' containing a list of strings."),
        ("user", "Stats: {input_stats}\n\nKey Narrative Beats (JSON):")
    ])
    
    chain = prompt | llm | parser
    return chain

def check_recall(draft: str, beats: List[str]):
    """
    Simple check to see if beats are present in the draft.
    For a more robust check, we could use an LLM, but string matching is faster for now.
    actually, let's use a quick LLM check for semantic matching.
    """
    llm = ChatOllama(model="mistral", temperature=0) # Mistral is good for checking
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Strict Editor. Check if the following FACTS are mentioned in the ARTICLE. Return 'YES' or 'NO' for each fact."),
        ("user", "Facts: {beats}\n\nArticle: {draft}\n\nOutput ONLY a JSON list of booleans, e.g. [true, false, true].")
    ])
    
    # We'll just define a bespoke chain here or do it inline
    # For now, let's keep it simple and return the Analyst chain only.
    pass
