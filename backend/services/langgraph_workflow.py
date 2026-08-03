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


from datetime import datetime

def extraction_node(state: ComplaintState):
    today = datetime.today().strftime("%Y-%m-%d")

    prompt = f"""
You are a pharmaceutical complaint data extraction engine.

Extract structured complaint information from the text below:

\"\"\"{state['raw_text']}\"\"\"

Return STRICT flat JSON with EXACTLY these keys:

complaint_source
customer_name
product_name
product_strength
batch_number
affected_quantity
manufacturing_date
expiry_date
complaint_date
originating_site
impacted_materials
complaint_category
description
structured_summary

IMPORTANT BUSINESS RULES:

1. If a company name appears before the word "reported",
   extract that as customer_name.
   In this case, complaint_source = "Pharmacy".

2. complaint_source must be one of:
   Pharmacy, Email, Distributor, Hospital

3. If affected_quantity is not mentioned:
   use "12 tablets".

4. If originating_site is not mentioned:
   use "Manufacturing".

5. If impacted_materials is not mentioned:
   use "Primary Packaging (Bottle)".

6. If complaint_date not mentioned:
   use "{today}"

7. complaint_category:
   If broken/damaged tablets → "Product Defect"

8. Return flat JSON only.
9. Do NOT nest objects.
10. Return valid JSON only.

Example format:

{{
  "complaint_source": "Pharmacy",
  "customer_name": "ABC Pharma",
  "product_name": "Paracetamol 500mg",
  "product_strength": "500mg",
  "batch_number": "B123",
  "affected_quantity": "12 tablets",
  "manufacturing_date": "Jan 2025",
  "expiry_date": "Jan 2027",
  "complaint_date": "{today}",
  "originating_site": "Manufacturing",
  "impacted_materials": "Primary Packaging (Bottle)",
  "complaint_category": "Product Defect",
  "description": "Broken tablets inside bottle",
  "structured_summary": "ABC Pharma reported broken tablets in batch B123 of Paracetamol 500mg."
}}
"""
    result = call_llm(prompt)
    return {"extracted": extract_json(result)}


def risk_node(state: ComplaintState):
    prompt = f"""
You are a pharmaceutical risk assessment AI.

Analyze the following complaint data:

{state['extracted']}

Return STRICT flat JSON with EXACTLY these keys:

severity
priority
suggested_action
initial_risk_assessment

Rules:
- severity must be: Low, Moderate, High, Critical
- priority must be: Low, Medium, High
- Return flat JSON only.
- Return only valid JSON.

Example:

{{
  "severity": "High",
  "priority": "High",
  "suggested_action": "",
  "initial_risk_assessment": ""
}}
"""
    result = call_llm(prompt)
    return {"risk": extract_json(result)}


graph = StateGraph(ComplaintState)

graph.add_node("extract", extraction_node)
graph.add_node("risk", risk_node)

graph.set_entry_point("extract")
graph.add_edge("extract", "risk")

app_graph = graph.compile()