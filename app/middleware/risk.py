# app/middleware/risk.py

from app.middleware.base import Middleware

class RiskMiddleware:

    name = "RiskMiddleware"

    def process(self, state: dict) -> dict:

        message = state.get("message", "").lower()
        tenant = state.get("tenant_id", "")
        intent = state.get("intent", "")

        risk_score = 0
        risk_flags = []

        # ==============================
        # 1️ Emergency Detection
        # ==============================

        emergency_keywords = [
            "chest pain",
            "bleeding",
            "emergency",
            "can't breathe",
            "severe pain",
            "stroke",
            "heart attack"
        ]

        if any(word in message for word in emergency_keywords):
            risk_score += 70
            risk_flags.append("Emergency language detected")

        # ==============================
        # 2️ Sensitive Appointment Types
        # ==============================

        high_risk_terms = [
            "surgery",
            "operation",
            "biopsy",
            "oncology",
            "cardiac"
        ]

        if any(word in message for word in high_risk_terms):
            risk_score += 25
            risk_flags.append("High-impact medical procedure")

        # ==============================
        # 3️Intent-Based Risk
        # ==============================

        if intent == "cancel" and "surgery" in message:
            risk_score += 20
            risk_flags.append("Cancellation of surgical appointment")

        # ==============================
        # 4️ Tenant Sensitivity
        # ==============================

        if tenant in ["restricted_tenant", "vip_tenant"]:
            risk_score += 15
            risk_flags.append("Restricted tenant context")

        # ==============================
        # 5️Final Risk Routing
        # ==============================

        state["risk_score"] = risk_score
        state["risk_flags"] = risk_flags

        if risk_score >= 70:
            state["terminal_status"] = "ESCALATE"
            state["risk_reason"] = "Critical threshold exceeded"
            return state

        if 30 <= risk_score < 70:
            state["terminal_status"] = "WAITING_APPROVAL"
            state["risk_reason"] = "Moderate risk requires oversight"
            return state

        return state