from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Output Models
class FactOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    errors: List[str] = Field(description="List of factual errors")

class StyleOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    feedback: str = Field(description="Critique on tone and excitement")

class BiasOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    issues: List[str] = Field(description="List of bias/fairness issues")

# 1. Fact Checker (Strict Mistral) - Same as original Judge but specialized
def get_fact_checker():
    llm = ChatOllama(model="mistral", temperature=0.0)
    parser = JsonOutputParser(pydantic_object=FactOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Fact Checker. Verify the Draft against the Stats. Focus ONLY on numbers and names. Return JSON."),
        ("user", "Stats: {stats}\nDraft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 2. Editor-in-Chief (Journalistic Standards)
def get_editor_in_chief():
    llm = ChatOllama(model="mistral", temperature=0.7)
    parser = JsonOutputParser(pydantic_object=StyleOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Editor-in-Chief. Grade the article on Journalistic Quality.\n\nCRITERIA:\n1. No Hallucinations: Did it use the wrong team name (e.g. calling Warriors 'Raptors')? FAIL immediately if so.\n2. Context: Did it mention the stakes (Series score, winning streak)?\n3. Flow: Does it read like a real human sportswriter?\n\nPASS only if it meets high editorial standards."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 3. Bias Watchdog (Neutral Mistral)
def get_bias_watchdog():
    llm = ChatOllama(model="mistral", temperature=0.1)
    parser = JsonOutputParser(pydantic_object=BiasOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Safety Guardrail. Check for unfair bias against losing teams or offensive language. PASS if neutral/fair."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser
