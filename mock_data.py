# mock_data.py
# Realistic mock responses for Grafana and Moogsoft
# These look exactly like real API responses - audience won't know the difference

import random
from datetime import datetime, timedelta

# ─── Mock Grafana Metrics ────────────────────────────────────────────────────

SERVICES = ["payment-service", "auth-service", "order-service", "api-gateway", "user-service"]

GRAFANA_METRICS = {
    "payment-service": {
        "cpu_percent": 87.4,
        "memory_percent": 72.1,
        "latency_p99_ms": 1423,
        "latency_p50_ms": 340,
        "error_rate_percent": 4.2,
        "requests_per_sec": 312,
        "status": "degraded",
        "spike_since": "14:07",
        "note": "Latency spiked from 180ms baseline at 14:07"
    },
    "auth-service": {
        "cpu_percent": 41.2,
        "memory_percent": 55.8,
        "latency_p99_ms": 210,
        "latency_p50_ms": 95,
        "error_rate_percent": 0.8,
        "requests_per_sec": 890,
        "status": "warning",
        "spike_since": None,
        "note": "Slightly elevated error rate, within acceptable range"
    },
    "order-service": {
        "cpu_percent": 23.5,
        "memory_percent": 38.2,
        "latency_p99_ms": 145,
        "latency_p50_ms": 60,
        "error_rate_percent": 0.1,
        "requests_per_sec": 540,
        "status": "healthy",
        "spike_since": None,
        "note": "All metrics within normal thresholds"
    },
    "api-gateway": {
        "cpu_percent": 61.8,
        "memory_percent": 68.4,
        "latency_p99_ms": 890,
        "latency_p50_ms": 210,
        "error_rate_percent": 2.1,
        "requests_per_sec": 1420,
        "status": "warning",
        "spike_since": "13:55",
        "note": "Elevated latency since 13:55, correlates with downstream payment-service issues"
    },
    "user-service": {
        "cpu_percent": 18.3,
        "memory_percent": 29.7,
        "latency_p99_ms": 98,
        "latency_p50_ms": 42,
        "error_rate_percent": 0.05,
        "requests_per_sec": 230,
        "status": "healthy",
        "spike_since": None,
        "note": "Nominal performance"
    }
}

# ─── Mock Moogsoft Alerts ────────────────────────────────────────────────────

MOOGSOFT_ALERTS = [
    {
        "alert_id": "MOOG-2847",
        "severity": "CRITICAL",
        "service": "payment-service",
        "type": "DB Connection Pool Exhausted",
        "message": "DB connection pool at 100% capacity. New connections being rejected.",
        "fired_at": "14:09",
        "duration_min": 47,
        "suppressed": False
    },
    {
        "alert_id": "MOOG-2851",
        "severity": "HIGH",
        "service": "payment-service",
        "type": "P99 Latency Threshold Breached",
        "message": "p99 latency exceeded 1000ms threshold. Current: 1423ms.",
        "fired_at": "14:11",
        "duration_min": 45,
        "suppressed": False
    },
    {
        "alert_id": "MOOG-2853",
        "severity": "HIGH",
        "service": "api-gateway",
        "type": "Downstream Timeout",
        "message": "api-gateway reporting timeouts on payment-service calls. Timeout rate: 12%.",
        "fired_at": "14:13",
        "duration_min": 43,
        "suppressed": False
    },
    {
        "alert_id": "MOOG-2840",
        "severity": "MEDIUM",
        "service": "auth-service",
        "type": "Error Rate Above Baseline",
        "message": "Error rate at 0.8%, baseline is 0.2%. Monitoring.",
        "fired_at": "13:52",
        "duration_min": 64,
        "suppressed": False
    },
    {
        "alert_id": "MOOG-2831",
        "severity": "LOW",
        "service": "api-gateway",
        "type": "CPU Spike",
        "message": "CPU at 61%, soft threshold is 60%. Non-critical.",
        "fired_at": "13:40",
        "duration_min": 76,
        "suppressed": True
    }
]


def get_grafana_metrics(service_name: str) -> dict:
    """Returns mock Grafana metrics for a given service."""
    service_name = service_name.lower().strip()

    # fuzzy match
    for key in GRAFANA_METRICS:
        if key in service_name or service_name in key:
            data = GRAFANA_METRICS[key].copy()
            # add tiny random variation so it never looks static
            data["cpu_percent"] = round(data["cpu_percent"] + random.uniform(-1.2, 1.2), 1)
            data["latency_p99_ms"] = int(data["latency_p99_ms"] + random.randint(-20, 20))
            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["source"] = "Grafana (mock)"
            return {"service": key, "metrics": data}

    # unknown service — return generic healthy
    return {
        "service": service_name,
        "metrics": {
            "cpu_percent": round(random.uniform(15, 35), 1),
            "memory_percent": round(random.uniform(30, 55), 1),
            "latency_p99_ms": random.randint(80, 200),
            "error_rate_percent": round(random.uniform(0.01, 0.3), 2),
            "status": "healthy",
            "note": "No anomalies detected",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Grafana (mock)"
        }
    }


def get_moogsoft_alerts(service_name: str = None, severity: str = None) -> list:
    """Returns mock Moogsoft alerts, optionally filtered by service or severity."""
    alerts = MOOGSOFT_ALERTS.copy()

    if service_name:
        service_name = service_name.lower().strip()
        alerts = [
            a for a in alerts
            if service_name in a["service"] or a["service"] in service_name
        ]

    if severity:
        alerts = [a for a in alerts if a["severity"] == severity.upper()]

    # only return non-suppressed by default
    active = [a for a in alerts if not a["suppressed"]]
    return active if active else alerts
