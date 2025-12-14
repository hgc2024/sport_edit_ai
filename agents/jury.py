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

# 2. Style Critic (Creative Llama 3.2)
def get_style_critic():
    llm = ChatOllama(model="llama3.2", temperature=0.7)
    parser = JsonOutputParser(pydantic_object=StyleOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Editor. content must be exciting, energetic, and sound like a professional sportscaster. PASS if good, FAIL if boring or robotic."),
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
