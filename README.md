Project Setup & Startup Instructions
1. Prerequisites

Ensure the following are installed:

Python 3.10+ (recommended 3.11)

Git

Virtual environment support (venv or uv)

Windows PowerShell, Git Bash, or macOS/Linux terminal

Optional:

VS Code (recommended for development)

2. Clone the Repository
git clone https://github.com/<gavinshklanka>/health_orchestrator.git
cd health_orchestrator
3. Create Virtual Environment
Option A — Standard venv
python -m venv .venv

Activate:

Windows (PowerShell):

.venv\Scripts\activate

Git Bash:

source .venv/Scripts/activate

macOS/Linux:

source .venv/bin/activate
Option B — If using uv (as in this project)
uv venv
source .venv/Scripts/activate
4. Install Dependencies

If you have a requirements file:

pip install -r requirements.txt

If not, manually install core dependencies:

pip install fastapi uvicorn langgraph jinja2 python-multipart

If using LangChain components:

pip install langchain
5. Database Initialization

This project uses SQLite.

On first run, ensure:

health_orchestrator.db exists in project root
OR

Your app contains auto-create logic for tables

If needed, manually create the DB file:

touch health_orchestrator.db

Or let the application initialize tables automatically if implemented.

6. Start the Application

From the project root:

uvicorn app.web.app:app --reload

Explanation:

app.web.app → module path

app → FastAPI instance

--reload → development hot reload

7. Access the Application

Open browser:

http://127.0.0.1:8000/

Key routes:

Route	Description
/	Governance Dashboard
/appointment	Create Appointment Run
/approvals	Approval Queue
/session/{run_id}	Run Execution View
/docs	FastAPI Swagger API
8. Testing Governance Scenarios

Use these example test inputs:

Normal Automation

Message:

Reschedule my dental cleaning.

Expected:

Status → RUNNING → COMPLETED

Moderate Risk (HITL Trigger)

Message:

Cancel my surgery next week.

Expected:

Status → WAITING_APPROVAL

Appears in Approval Queue

Requires manual approval

Emergency Escalation

Message:

I have chest pain and need help immediately.

Expected:

Status → ESCALATED

Pulse indicator in session view

Visible in escalated column

Restricted Tenant

Use:

tenant_id = restricted_tenant

Expected:

WAITING_APPROVAL regardless of intent

9. Approving a Run

Navigate to /approvals

Click Approve

System resumes execution

Redirects to session view

Status transitions to COMPLETED

10. Stopping the Server

Press:

CTRL + C
Optional Production Deployment

For production:

uvicorn app.web.app:app --host 0.0.0.0 --port 8000

Or run behind:

Nginx

Docker

Cloud provider (Azure, AWS, GCP)

SQLite can be replaced with:

PostgreSQL

MySQL

Enterprise DB

Middleware architecture remains unchanged.

Development Notes

State is passed via LangGraph.

Middleware stack governs all tool execution.

Approval resumes execution via re-invocation.

Dashboard metrics compute live from DB.

Audit trail logs stored per run.

Troubleshooting
Import errors:

Ensure:

PYTHONPATH includes project root

Run from project root directory.

Template errors:

Confirm:

app/templates/

exists and contains all HTML files.

DB errors:

Verify health_orchestrator.db path matches get_connection() configuration.

Agentic Appointment Engine

Governance-First AI Orchestration Platform

Overview

The Agentic Appointment Engine is a governance-oriented AI orchestration system built using FastAPI, LangGraph, and a structured middleware architecture.

This system demonstrates how AI-powered workflows can be executed under strict policy controls, human-in-the-loop oversight, risk evaluation, and audit traceability.

Rather than functioning as a simple chatbot or automation tool, this platform acts as a controlled execution environment where:

Every workflow is state-managed

Every decision is observable

Every high-risk action is interruptible

Every outcome is auditable

The project was designed to model how enterprise-grade AI systems should behave in regulated or risk-sensitive environments.

Core Architecture
1. Graph-Based Orchestration (LangGraph)

Workflows are modeled as a state graph:

Intent classification

Conditional routing

Tool preparation

Human-in-the-loop interrupt nodes

Controlled execution

The graph structure enables deterministic state transitions and transparent execution paths.

2. Governance Middleware Stack

All tool execution flows through a structured middleware pipeline:

Authentication Middleware

Validation Middleware

Redaction Middleware

Policy Middleware

Risk Middleware

Tool Wrapper Middleware

This layered control model ensures:

Policy enforcement before execution

Risk-based interruption

Escalation handling

Structured lifecycle logging

No tool executes outside of governance controls.

3. Human-in-the-Loop (HITL) Control

The engine supports interruption and controlled resumption:

Draft action prepared

Workflow pauses at approval stage

Human approval recorded

Execution resumes through the graph

Approval events are stored with metadata including:

Approved by

Policy level

Approval timestamp

Summary of changes

This creates measurable oversight latency and accountability metrics.

4. Risk-Aware Routing

RiskMiddleware dynamically evaluates:

Emergency language

Tenant restrictions

High-impact intents

Policy violations

Possible terminal states:

RUNNING

WAITING_APPROVAL

ESCALATED

FAILED

COMPLETED

This enables real-time governance responses instead of static rule switches.

5. Executive Dashboard

The platform includes a governance control plane displaying:

Automation rate

Human intervention rate

Escalation frequency

Oversight latency

Audit trail density

Active workflow segmentation

Operational views include:

Active workflows

Pending human review

Escalated risk

Recently completed runs

The system is observable, not opaque.

6. Audit & Traceability

Each run logs lifecycle events:

Middleware execution

Errors

Approvals

Status transitions

Audit density is visible per session.

This supports defensibility, compliance alignment, and incident review.

Technical Stack

Backend:

FastAPI

LangGraph

SQLite

Jinja2 Templates

Architecture Patterns:

State-driven orchestration

Middleware enforcement

Deterministic routing

Human-in-the-loop control

Governance telemetry

Why Governance-First AI?

Most AI systems optimize for:

Speed

Automation rate

Output quality

Few optimize for:

Control

Auditability

Risk containment

Escalation transparency

Policy alignment

This system demonstrates that AI execution can be designed as controlled infrastructure rather than unbounded automation.

Business Value by Sector
Healthcare

Value:

Risk-aware patient workflow automation

Human approval before high-impact actions

Escalation for emergency indicators

Audit trail for regulatory compliance

Supports:

Clinical triage assistants

Appointment automation

Prior authorization workflows

Care navigation tools

Governance reduces liability exposure and compliance risk.

Banking & Financial Services

Value:

Approval layers before financial impact actions

Tenant-based restrictions

Transaction risk escalation

Measurable oversight latency

Supports:

Loan processing assistants

Fraud review automation

Credit decision workflows

Internal compliance tooling

This aligns with audit-heavy regulatory environments.

Insurance

Value:

Controlled claims routing

Risk-based escalation logic

Human review for high-value adjustments

Full audit logging

Supports:

Claims triage

Underwriting automation

Policy amendment workflows

Governance reduces regulatory and reputational exposure.

Enterprise Operations

Value:

Policy-enforced internal automations

Structured workflow lifecycle

Escalation thresholds

Executive observability dashboards

Supports:

HR request systems

Procurement approvals

IT service workflows

Vendor risk analysis

Renewable Energy & Utilities

Value:

Incident escalation detection

Structured human oversight

Tenant-level restrictions

Risk-triggered workflow interruption

Supports:

Grid incident workflows

Maintenance ticket routing

Compliance management

The Governance Paradox

Governance-first AI systems are not always immediately financially attractive.

Why?

Because governance:

Slows automation at critical points

Adds human review friction

Increases engineering complexity

Prioritizes safety over velocity

Pure automation often looks more profitable in the short term.

However:

Poorly governed AI systems introduce:

Legal exposure

Regulatory penalties

Reputational risk

Operational instability

Hidden compliance costs

The long-term financial model favors:

Controlled intelligent systems
Over unbounded automation

Infrastructure designed with governance at the core allows organizations to scale AI responsibly rather than retrofitting controls after failure.

Strategic Value Proposition

This project demonstrates that:

AI execution engines can be built with governance as a first-class architectural principle.

When designed correctly:

Policy is embedded, not bolted on

Risk is evaluated before action

Human oversight is measurable

Escalation is systemic

Auditability is native

This is not a chatbot demo.

It is a model for how intelligent business systems should be architected in regulated or high-risk environments.

Conclusion

The Agentic Appointment Engine represents a governance-first AI orchestration framework.

It demonstrates:

Structured control over automation

Risk-based workflow interruption

Human-in-the-loop integration

Executive-level observability

Audit-backed defensibility









#Dev Notes - pls ignore the mess 

Do not redesign the architecture.
Continue from Phase A — Expose Engine Signal.
Start with Dashboard detail pane expansion.


uv run uvicorn app.web.server:app --reload

uv run python -m app.cli.main

Checking db
dir *.db
uv run python
import sqlite3

conn = sqlite3.connect("health_orchestrator.db")
cursor = conn.cursor()

print("TOOL LEDGER ROWS:")
for row in cursor.execute("SELECT * FROM tool_ledger"):
    print(row)

print("\nAPPROVAL ROWS:")
for row in cursor.execute("SELECT * FROM approvals"):
    print(row)

conn.close()




