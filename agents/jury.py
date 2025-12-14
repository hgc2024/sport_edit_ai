from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Output Models
class FactOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    errors: List[str] = Field(description="List of factual errors found (e.g. numeric mismatches). Empty if PASS.")

class StyleOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    score: int = Field(description="Quality Score between 1-10")
    feedback: str = Field(description="Detailed critique")

class BiasOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    issues: List[str] = Field(description="List of bias issues found")

class SeoOutput(BaseModel):
    score: int = Field(description="SEO Score 0-100")
    suggestions: List[str] = Field(description="List of improvements")

class EngagementOutput(BaseModel):
    score: int = Field(description="Engagement Score 1-10")
    critique: str = Field(description="Feedback")

class SafetyOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    flags: List[str] = Field(description="List of unsafe content flags")

# 1. Fact Checker (Mistral)
def get_fact_checker():
    llm = ChatOllama(model="mistral", temperature=0.1)
    parser = JsonOutputParser(pydantic_object=FactOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict Fact Checker. Compare the Draft against the Stats. Verify numbers. Return JSON."),
        ("user", "Stats: {stats}\n\nDraft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 2. Editor-in-Chief (Journalistic Standards)
def get_editor_in_chief():
    llm = ChatOllama(model="mistral", temperature=0.7)
    parser = JsonOutputParser(pydantic_object=StyleOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Editor-in-Chief. Grade the article (1-10). Check for Hallucinations ('Raptors' vs 'Warriors') and stakes. Return JSON."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 3. Bias Watchdog
def get_bias_watchdog():
    llm = ChatOllama(model="mistral", temperature=0.1)
    parser = JsonOutputParser(pydantic_object=BiasOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Check for unfair bias or offensive language. Return JSON."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 4. SEO Strategist
def get_seo_strategist():
    llm = ChatOllama(model="mistral", temperature=0.3)
    parser = JsonOutputParser(pydantic_object=SeoOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "SEO Strategist. Check keywords and density. Return JSON."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 5. Engagement Editor
def get_engagement_editor():
    llm = ChatOllama(model="mistral", temperature=0.6)
    parser = JsonOutputParser(pydantic_object=EngagementOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Engagement Editor. Check hook and readability. Return JSON."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 6. Brand Safety
def get_brand_safety():
    llm = ChatOllama(model="mistral", temperature=0.1)
    parser = JsonOutputParser(pydantic_object=SafetyOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Brand Safety. Check for toxicity. Return JSON."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser
