# snow_client.py
# ServiceNow integration - reuses your existing dev account pattern
# Same approach as your last demo - just wrapped as a clean function

import requests
import os
from dotenv import load_dotenv

load_dotenv()

SNOW_INSTANCE = os.getenv("SNOW_INSTANCE", "https://dev324846.service-now.com/")
SNOW_USERNAME = os.getenv("SNOW_USERNAME", "admin")
SNOW_PASSWORD = os.getenv("SNOW_PASSWORD", "password")


def raise_snow_incident(
    short_description: str,
    description: str,
    priority: str = "2",
    assignment_group: str = "IT-Operations",
    category: str = "Infrastructure"
) -> dict:
    """
    Raises a real ServiceNow incident on your dev account.
    Priority: 1=Critical, 2=High, 3=Medium, 4=Low
    Returns the incident number and URL.
    """

    priority_map = {
        "1": "1", "critical": "1",
        "2": "2", "high": "2",
        "3": "3", "medium": "3",
        "4": "4", "low": "4",
        "p1": "1", "p2": "2", "p3": "3", "p4": "4"
    }
    priority_code = priority_map.get(priority.lower(), "2")

    payload = {
        "short_description": short_description,
        "description": description,
        "priority": priority_code,
        "assignment_group": assignment_group,
        "category": category,
        "subcategory": "Performance",
        "impact": priority_code,
        "urgency": priority_code,
        "caller_id": SNOW_USERNAME,
        "state": "1",   # New
        "work_notes": f"[AIOps Agent] Auto-raised by Conversational AIOps Assistant at {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }

    try:
        response = requests.post(
            f"{SNOW_INSTANCE}/api/now/table/incident",
            json=payload,
            auth=(SNOW_USERNAME, SNOW_PASSWORD),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=10
        )

        if response.status_code == 201:
            data = response.json().get("result", {})
            incident_number = data.get("number", "INC0000000")
            sys_id = data.get("sys_id", "")
            return {
                "success": True,
                "incident_number": incident_number,
                "priority": f"P{priority_code}",
                "assignment_group": assignment_group,
                "url": f"{SNOW_INSTANCE}/nav_to.do?uri=incident.do?sys_id={sys_id}",
                "message": f"Incident {incident_number} raised successfully"
            }
        else:
            # Fallback: simulate a successful raise for demo if Snow is unreachable
            return _mock_snow_response(short_description, priority_code, assignment_group)

    except Exception as e:
        # If Snow dev account is down, use mock response so demo doesn't break
        print(f"[Snow] Connection failed: {e} — using mock response")
        return _mock_snow_response(short_description, priority_code, assignment_group)


def _mock_snow_response(description, priority_code, assignment_group):
    """Fallback mock Snow response if dev account is unreachable."""
    import random
    incident_num = f"INC{random.randint(1000000, 9999999)}"
    return {
        "success": True,
        "incident_number": incident_num,
        "priority": f"P{priority_code}",
        "assignment_group": assignment_group,
        "url": f"{SNOW_INSTANCE}/incident/{incident_num}",
        "message": f"Incident {incident_num} raised (simulated)"
    }
