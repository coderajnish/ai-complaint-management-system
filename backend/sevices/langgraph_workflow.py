from langgraph.graph import StateGraph
from typing import TypedDict
from services.ai_service import call_llm
import json, re


class ComplaintState(TypedDict):
    raw_text: str
    extracted: dict
    risk: dict


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group()) if match else {}


def extraction_node(state: ComplaintState):
    prompt = f"""
Extract structured complaint JSON from:
{state['raw_text']}
Return JSON only.
"""
    result = call_llm(prompt)
    return {"extracted": extract_json(result)}


def risk_node(state: ComplaintState):
    prompt = f"""
Classify risk for:
{state['extracted']}

Return JSON:
severity, priority, initial_risk_assessment
"""
    result = call_llm(prompt)
    return {"risk": extract_json(result)}


graph = StateGraph(ComplaintState)

graph.add_node("extract", extraction_node)
graph.add_node("risk", risk_node)

graph.set_entry_point("extract")
graph.add_edge("extract", "risk")
