# agent.py
# LangChain agent powered by Gemini 2.5 Flash
# Tools: grafana_metrics | moogsoft_alerts | raise_incident

import os
import json
from dotenv import load_dotenv

#from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from mock_data import get_grafana_metrics, get_moogsoft_alerts
from snow_client import raise_snow_incident

load_dotenv()

# ─── Tool Definitions ────────────────────────────────────────────────────────

@tool
def grafana_metrics(service_name: str) -> str:
    """
    Fetches real-time performance metrics from Grafana for a given service.
    Returns CPU, memory, latency (p50/p99), error rate, and request rate.
    Use this when the user asks about performance, slowness, or health of any service.
    """
    result = get_grafana_metrics(service_name)
    return json.dumps(result, indent=2)


@tool
def moogsoft_alerts(service_name: str = "") -> str:
    """
    Fetches active alerts from Moogsoft AIOps platform.
    Optionally filter by service name. Returns alert ID, severity, type, and message.
    Use this to check what alerts are currently firing and correlate with user questions.
    """
    alerts = get_moogsoft_alerts(service_name=service_name if service_name else None)
    return json.dumps({"active_alerts": alerts, "count": len(alerts)}, indent=2)


@tool
def raise_incident(
    short_description: str,
    description: str,
    priority: str,
    assignment_group: str = "IT-Operations"
) -> str:
    """
    Raises a ServiceNow incident ticket.
    Use this ONLY when the user explicitly asks to raise, create, or open an incident.
    Priority options: P1 (Critical), P2 (High), P3 (Medium), P4 (Low).
    assignment_group: team to assign the ticket to (e.g. 'DB-Ops', 'Network-Ops', 'IT-Operations').
    """
    result = raise_snow_incident(
        short_description=short_description,
        description=description,
        priority=priority,
        assignment_group=assignment_group
    )
    return json.dumps(result, indent=2)


# ─── Agent Setup ────────────────────────────────────────────────────────────

TOOLS = [grafana_metrics, moogsoft_alerts, raise_incident]

SYSTEM_PROMPT = """You are an intelligent AIOps assistant integrated with Grafana (metrics) and Moogsoft (alerts).

Your job:
1. Answer questions about infrastructure health, service performance, and active alerts
2. Proactively correlate metrics with alerts to identify root causes
3. Suggest remediation steps based on what you find
4. Raise ServiceNow incidents ONLY when the user explicitly asks you to

Rules:
- Always call grafana_metrics AND moogsoft_alerts together when diagnosing an issue
- Be concise but specific — include actual numbers from the data
- Format your final answer clearly: Finding → Root Cause → Suggested Action
- When you raise an incident, confirm the ticket number and assignment group
- Sound like an expert SRE, not a chatbot

Current context: You are assisting an AIOps team. Grafana and Moogsoft data is live.
"""

def build_agent() -> AgentExecutor:
    """Builds and returns the LangChain agent with Gemini 2.5 Flash."""

    llm = ChatOpenAI(
        model="deepseek/deepseek-chat",   # 🔥 FREE + high token model
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.1,
        max_tokens=2048   # 🔥 increase token limit
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,           # prints tool calls to terminal - useful for debugging
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True   # needed for showing tool calls in Streamlit
    )
