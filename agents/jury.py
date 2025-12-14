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
    score: int = Field(description="Quality Score between 1-10")
    feedback: str = Field(description="Detailed critique")

# ... (Fact Checker remains same)

# 2. Editor-in-Chief (Journalistic Standards)
def get_editor_in_chief():
    llm = ChatOllama(model="mistral", temperature=0.7)
    parser = JsonOutputParser(pydantic_object=StyleOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Editor-in-Chief. Grade the article on Journalistic Quality (1-10).\n\nSCORING CRITERIA:\n- 10: Perfect Context, Great Flow, Zero Errors.\n- 8-9: Good Context, minor flow issues.\n- 6-7: Passable, but could be better.\n- 1-5: FAIL. Hallucinations (wrong team names), Missing Stakes, or Robotic.\n\nCRITICAL CHECKS (Automatic FAIL/Score 1):\n1. Hallucinations: Did it call Warriors 'Raptors'?\n2. Context: Did it fail to mention the Series Score or Streak?\n\nRETURN JSON with status (PASS/FAIL), score (int), and feedback."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# ... (Existing Output Models)

class SeoOutput(BaseModel):
    score: int = Field(description="SEO Score 0-100")
    suggestions: List[str] = Field(description="List of keyword/structure improvements")

class EngagementOutput(BaseModel):
    score: int = Field(description="Engagement Score 1-10")
    critique: str = Field(description="Feedback on hook and readability")

class SafetyOutput(BaseModel):
    status: str = Field(description="PASS or FAIL")
    flags: List[str] = Field(description="List of unsafe content flags")

# ... (Existing Fact/Editor Agents)

# 3. Bias Watchdog (Neutral Mistral)
def get_bias_watchdog():
    llm = ChatOllama(model="mistral", temperature=0.1)
    parser = JsonOutputParser(pydantic_object=BiasOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Safety Guardrail. Check for unfair bias against losing teams or offensive language. PASS if neutral/fair."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 4. SEO Strategist (Growth Division)
def get_seo_strategist():
    llm = ChatOllama(model="mistral", temperature=0.3)
    parser = JsonOutputParser(pydantic_object=SeoOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an SEO Strategist. Optimize for Search Traffic.\n\nCRITERIA:\n1. Keywords: Are team names (e.g. 'Lakers', 'Warriors') used in the first 2 sentences?\n2. Entity Density: Are key player names mentioned?\n3. Structure: Is the content structured for skimmers?\n\nScore 0-100. If < 70, provide specific keyword insertion suggestions."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 5. Engagement Editor (Growth Division)
def get_engagement_editor():
    llm = ChatOllama(model="mistral", temperature=0.6)
    parser = JsonOutputParser(pydantic_object=EngagementOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Engagement Editor. Optimize for Time-on-Page.\n\nCRITERIA:\n1. The Hook: Is the first sentence boring? (e.g. 'The game was played...') => FAIL. It must be punchy.\n2. Readability: Are paragraphs too long?\n3. CTA: Does it end with a forward-looking thought?\n\nScore 1-10. If < 7, fail."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser

# 6. Brand Safety Officer (Standards Division)
def get_brand_safety():
    llm = ChatOllama(model="mistral", temperature=0.1)
    parser = JsonOutputParser(pydantic_object=SafetyOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Brand Safety Officer. Protect Ad Revenue.\n\nCRITERIA:\n1. Toxicity: Any hate speech or slurs? (Automatic FAIL)\n2. Sentiment: Is criticism of the losing team too harsh/abusive? (e.g. 'Disgrace to the sport' is UNSAFE)\n3. Controversy: Any political metaphors?\n\nStrict Veto Power. PASS only if Safe for All Advertisers."),
        ("user", "Draft: {draft}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    return prompt | llm | parser
