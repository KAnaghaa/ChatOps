# AIOps Conversational Assistant — Setup Guide
# =============================================
# Copy-paste every command exactly as shown.

# ─── STEP 1: Project structure ───────────────────────────────────────────────
# Create a folder and put all 5 files inside it:
#
#   aiops-demo/
#   ├── app.py
#   ├── agent.py
#   ├── mock_data.py
#   ├── snow_client.py
#   ├── .env
#   └── requirements.txt

# ─── STEP 2: Get your free Gemini API key (2 minutes) ────────────────────────
# 1. Go to: https://aistudio.google.com
# 2. Sign in with any Google account
# 3. Click "Get API Key" → "Create API Key"
# 4. Copy the key

# ─── STEP 3: Create your .env file ──────────────────────────────────────────
# Create a file named exactly  .env  (no other extension) with this content:
#
#   GEMINI_API_KEY=AIzaSy...your_key_here...
#   SNOW_INSTANCE=https://yourinstance.service-now.com
#   SNOW_USERNAME=your_username
#   SNOW_PASSWORD=your_password

# ─── STEP 4: Install dependencies ───────────────────────────────────────────

cd aiops-demo
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# ─── STEP 5: Run the app ─────────────────────────────────────────────────────

streamlit run app.py

# App opens at: http://localhost:8501
# That's it. Start chatting!

# ─── DEMO SCRIPT (what to type during presentation) ─────────────────────────
#
# Q1: "Why is the payment service showing high latency since 2pm?"
#   → Agent calls Grafana + Moogsoft → finds DB pool exhaustion → explains root cause
#
# Q2: "What critical alerts are currently active?"
#   → Agent calls Moogsoft → lists MOOG-2847 (DB pool), MOOG-2851 (latency breach)
#
# Q3: "What's the health of api-gateway?"
#   → Agent calls Grafana → shows metrics → notes downstream impact from payment-service
#
# Q4: "Raise a P2 incident for the payment service DB issue"
#   → Agent calls ServiceNow → real ticket raised on your dev account
#   → Shows: INC0041823 | P2 | Assigned to DB-Ops
#
# Q5: "Which service has the highest error rate right now?"
#   → Agent checks all services → ranks by error rate → payment-service at 4.2%

# ─── TROUBLESHOOTING ─────────────────────────────────────────────────────────
#
# Error: "GEMINI_API_KEY not set"
#   → Make sure your .env file is in the SAME folder as app.py
#
# Error: "module langchain_google_genai not found"
#   → Run: pip install langchain-google-genai
#
# Snow tickets not raising:
#   → Check SNOW_INSTANCE url has no trailing slash
#   → snow_client.py has a mock fallback — demo won't break even if Snow is down
#
# Agent not calling tools:
#   → Check your Gemini key is valid at: https://aistudio.google.com
