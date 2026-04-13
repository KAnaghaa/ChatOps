# app.py
# Conversational AIOps Assistant — Streamlit UI
# Run: streamlit run app.py

import streamlit as st
import json
from agent import build_agent
from langchain_core.messages import HumanMessage, AIMessage

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AIOps Assistant",
    page_icon="🔍",
    layout="wide"
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
  /* Tool call pill styling */
  .tool-pill {
      display: inline-block;
      background: #1e293b;
      color: #7dd3fc;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 3px 10px;
      font-size: 12px;
      font-family: monospace;
      margin: 2px 4px 2px 0;
  }
  .tool-pill.snow { color: #86efac; border-color: #166534; background: #052e16; }
  .step-box {
      background: #0f172a;
      border-left: 3px solid #334155;
      border-radius: 4px;
      padding: 8px 12px;
      margin: 4px 0;
      font-size: 12px;
      color: #94a3b8;
      font-family: monospace;
  }
  /* Metric cards */
  .metric-row { display: flex; gap: 12px; margin: 8px 0; flex-wrap: wrap; }
  .metric-card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 8px 14px;
      min-width: 110px;
      text-align: center;
  }
  .metric-val { font-size: 18px; font-weight: 600; color: #f1f5f9; }
  .metric-val.red { color: #f87171; }
  .metric-val.yellow { color: #fbbf24; }
  .metric-val.green { color: #4ade80; }
  .metric-lbl { font-size: 10px; color: #64748b; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔍 AIOps Assistant")
    st.markdown("**Powered by Gemini 2.5 Flash**")
    st.divider()

    st.markdown("**Connected systems**")
    st.success("Grafana  (metrics)")
    st.success("Moogsoft  (alerts)")
    st.success("ServiceNow  (ITSM)")
    st.divider()

    st.markdown("**Try asking:**")
    example_questions = [
        "Why is payment-service slow?",
        "Show active critical alerts",
        "What's the health of api-gateway?",
        "Raise a P2 incident for payment-service DB issue",
        "Which service has the highest error rate?",
        "Summarize all active alerts"
    ]
    for q in example_questions:
        if st.button(q, use_container_width=True, key=q):
            st.session_state["quick_input"] = q

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# ─── Session State ────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent" not in st.session_state:
    with st.spinner("Initializing AIOps agent..."):
        st.session_state.agent = build_agent()

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("## Conversational AIOps Assistant")
st.caption("Ask anything about your infrastructure — I'll check Grafana metrics and Moogsoft alerts in real time.")
st.divider()

# ─── Render Chat History ──────────────────────────────────────────────────────

def severity_color(severity: str) -> str:
    return {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(severity, "⚪")

def status_color_class(status: str) -> str:
    return {"healthy": "green", "warning": "yellow", "degraded": "red"}.get(status, "")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Show tool call steps if present
        if msg.get("tool_steps"):
            for step in msg["tool_steps"]:
                tool_name = step.get("tool", "")
                if "grafana" in tool_name:
                    st.markdown(f'<span class="tool-pill">⚡ Calling grafana_metrics tool...</span>', unsafe_allow_html=True)
                elif "moogsoft" in tool_name:
                    st.markdown(f'<span class="tool-pill">🚨 Calling moogsoft_alerts tool...</span>', unsafe_allow_html=True)
                elif "incident" in tool_name:
                    st.markdown(f'<span class="tool-pill snow">🎫 Calling raise_incident → ServiceNow...</span>', unsafe_allow_html=True)

        st.markdown(msg["content"])

        # Show metric visualization if grafana data was fetched
        if msg.get("grafana_data"):
            m = msg["grafana_data"].get("metrics", {})
            status_cls = status_color_class(m.get("status", ""))
            cpu_cls = "red" if m.get("cpu_percent", 0) > 80 else "yellow" if m.get("cpu_percent", 0) > 60 else "green"
            lat_cls = "red" if m.get("latency_p99_ms", 0) > 1000 else "yellow" if m.get("latency_p99_ms", 0) > 500 else "green"
            err_cls = "red" if m.get("error_rate_percent", 0) > 2 else "yellow" if m.get("error_rate_percent", 0) > 0.5 else "green"

            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-val {cpu_cls}">{m.get('cpu_percent', 'N/A')}%</div>
                    <div class="metric-lbl">CPU</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val {lat_cls}">{m.get('latency_p99_ms', 'N/A')}ms</div>
                    <div class="metric-lbl">p99 Latency</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val {err_cls}">{m.get('error_rate_percent', 'N/A')}%</div>
                    <div class="metric-lbl">Error Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val">{m.get('requests_per_sec', 'N/A')}</div>
                    <div class="metric-lbl">Req/sec</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Show Snow ticket if raised
        if msg.get("snow_result"):
            r = msg["snow_result"]
            st.success(f"✅ ServiceNow incident raised: **{r.get('incident_number')}** | {r.get('priority')} | Assigned to: {r.get('assignment_group')}")

# ─── Chat Input ───────────────────────────────────────────────────────────────

# handle sidebar quick-input buttons
default_input = st.session_state.pop("quick_input", "")
user_input = st.chat_input("Ask about your infrastructure...") or default_input

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        tool_placeholder = st.empty()
        response_placeholder = st.empty()

        tool_steps_log = []
        grafana_data = None
        snow_result = None

        with st.spinner("Agent thinking..."):
            try:
                result = st.session_state.agent.invoke({
                    "input": user_input,
                    "chat_history": st.session_state.chat_history
                })

                # Extract intermediate tool call steps
                intermediate = result.get("intermediate_steps", [])
                tool_html = ""
                for action, observation in intermediate:
                    tool_name = action.tool
                    tool_steps_log.append({"tool": tool_name})

                    if "grafana" in tool_name:
                        tool_html += '<span class="tool-pill">⚡ Calling grafana_metrics tool...</span>'
                        try:
                            obs_data = json.loads(observation)
                            grafana_data = obs_data
                        except:
                            pass
                    elif "moogsoft" in tool_name:
                        tool_html += '<span class="tool-pill">🚨 Calling moogsoft_alerts tool...</span>'
                    elif "incident" in tool_name:
                        tool_html += '<span class="tool-pill snow">🎫 Calling raise_incident → ServiceNow...</span>'
                        try:
                            obs_data = json.loads(observation)
                            snow_result = obs_data
                        except:
                            pass

                if tool_html:
                    tool_placeholder.markdown(tool_html, unsafe_allow_html=True)

                final_answer = result.get("output", "I couldn't process that request.")
                response_placeholder.markdown(final_answer)

                # Metric cards
                if grafana_data:
                    m = grafana_data.get("metrics", {})
                    status_cls = status_color_class(m.get("status", ""))
                    cpu_cls = "red" if m.get("cpu_percent", 0) > 80 else "yellow" if m.get("cpu_percent", 0) > 60 else "green"
                    lat_cls = "red" if m.get("latency_p99_ms", 0) > 1000 else "yellow" if m.get("latency_p99_ms", 0) > 500 else "green"
                    err_cls = "red" if m.get("error_rate_percent", 0) > 2 else "yellow" if m.get("error_rate_percent", 0) > 0.5 else "green"

                    st.markdown(f"""
                    <div class="metric-row">
                        <div class="metric-card">
                            <div class="metric-val {cpu_cls}">{m.get('cpu_percent', 'N/A')}%</div>
                            <div class="metric-lbl">CPU</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-val {lat_cls}">{m.get('latency_p99_ms', 'N/A')}ms</div>
                            <div class="metric-lbl">p99 Latency</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-val {err_cls}">{m.get('error_rate_percent', 'N/A')}%</div>
                            <div class="metric-lbl">Error Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-val">{m.get('requests_per_sec', 'N/A')}</div>
                            <div class="metric-lbl">Req/sec</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Snow ticket confirmation
                if snow_result:
                    st.success(f"✅ ServiceNow incident raised: **{snow_result.get('incident_number')}** | {snow_result.get('priority')} | Assigned to: {snow_result.get('assignment_group')}")

                # Save to history
                st.session_state.chat_history.append(HumanMessage(content=user_input))
                st.session_state.chat_history.append(AIMessage(content=final_answer))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "tool_steps": tool_steps_log,
                    "grafana_data": grafana_data,
                    "snow_result": snow_result
                })

            except Exception as e:
                err_msg = f"Agent error: {str(e)}"
                response_placeholder.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
