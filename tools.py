from typing import List, Dict, Any

def tool_checklist_builder(roles: List[str], constraints: Dict[str, Any]) -> Dict[str, Any]:
    steps = [
        {"phase": "Discovery", "items": [
        "Define role scope & success metrics",
        "Confirm budget, equity band, timeline, and location policy",
        "Write/approve JD drafts",
        ]},
        {"phase": "Sourcing", "items": [
        "Post roles to job boards + careers page",
        "Identify 50 target prospects for outbound",
        "Set up employee referral form",
        ]},
        {"phase": "Screening", "items": [
        "Resume screen rubric",
        "30-min recruiter screen template",
        "Technical/portfolio screen for engineers",
        ]},
        {"phase": "Assessment", "items": [
        "Structured interview loop + scorecards",
        "Take-home or live coding (founding engineer)",
        "Mini-build or prompt-engineering task (GenAI intern)",
        ]},
        {"phase": "Closing", "items": [
        "Reference checks",
        "Compensation & equity proposal",
        "Offer letter + start date",
        ]},
    ]
    if constraints.get("timeline_weeks"):
        steps.append({"phase": "Timeline", "items": [f"Target to fill within {constraints['timeline_weeks']} weeks"]})
    return {"roles": roles, "constraints": constraints, "phases": steps}
