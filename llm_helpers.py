import re
from typing import List, Dict, Any
from memory import Memory

CLARIFY_FIELDS = [
    ("budget", "What is your total budget per role (base + equity)? If unsure, give a range."),
    ("seniority", "What seniority level(s) are you targeting (e.g., founding/staff vs. intern/junior)?"),
    ("skills", "What must-have technical/functional skills should candidates have?"),
    ("timeline_weeks", "What is your ideal time-to-fill in weeks?"),
    ("location", "Are these roles remote, hybrid, or onsite? If onsite, where?"),
    ("process_prefs", "Any interview process preferences (take-home vs live, panel size)?"),
]


def generate_clarifying_questions(user_input: str, memory: Memory) -> List[str]:
    existing = set(memory.constraints.keys())
    qs = [q for key, q in CLARIFY_FIELDS if key not in existing]
    if not memory.roles_needed:
        qs.insert(0, "Which roles are you hiring for? Please list titles separated by commas.")
    return qs[:6]

def draft_job_description(role: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
    must = constraints.get("skills") or ["Python", "LLMs", "Start-up mindset"]
    if isinstance(must, str):
        must = [s.strip() for s in must.split(",") if s.strip()]
    return {
        "title": role,
        "summary": f"We are hiring a {role} to build and ship products in a fast-paced startup.",
        "responsibilities": [
            "Own end-to-end execution from design to deployment",
            "Collaborate with founders, product, and customers",
            "Maintain a high bar for quality and velocity",
        ],
        "requirements": [
            f"Proficiency in {', '.join(must)}",
            "Portfolio or Github that demonstrates impact",
            "Excellent communication and ownership",
        ],
        "compensation": constraints.get("budget", "Competitive salary and equity"),
        "location": constraints.get("location", "Remote-friendly"),
    }

def parse_roles_from_text(text: str):
    """
    Naive role extraction from free text.
    Example: "I need to hire a founding engineer and a GenAI intern"
    → ["founding engineer", "GenAI intern"]
    """
    text = text.lower()
    roles = []

    # Common joiners
    separators = re.split(r"\band\b|,|/|;", text)
    for part in separators:
        part = part.strip()
        # Heuristic: look for words like engineer, intern, designer, manager, etc.
        if any(job in part for job in ["engineer", "intern", "designer", "manager", "lead", "scientist", "developer"]):
            # Extract last 3 words (to catch "genai intern", "founding engineer")
            tokens = part.split()
            if len(tokens) >= 2:
                roles.append(" ".join(tokens[-3:]).strip())
            else:
                roles.append(part.strip())

    # Deduplicate
    return list(dict.fromkeys([r for r in roles if r]))
