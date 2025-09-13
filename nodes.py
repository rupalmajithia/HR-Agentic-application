from typing import TypedDict, Dict, Any
from memory import Memory
from tools import tool_checklist_builder
from llm_helpers import generate_clarifying_questions, draft_job_description

class HRState(TypedDict):
    user_input: str
    memory: Dict[str, Any]
    action: str
    result: Dict[str, Any]

from tools import tool_checklist_builder
from llm_helpers import generate_clarifying_questions, draft_job_description

def node_intake(state: HRState) -> HRState:
    mem = Memory(**state.get("memory", {}))
    user_input = state.get("user_input", "")
    if user_input:
        lower = user_input.lower()
        if "founding" in lower and "engineer" in lower and "Founding Engineer" not in mem.roles_needed:
            mem.roles_needed.append("Founding Engineer")
        if "intern" in lower and "genai" in lower and "GenAI Intern" not in mem.roles_needed:
            mem.roles_needed.append("GenAI Intern")
    questions = generate_clarifying_questions(user_input, mem)
    mem.clarifying_questions = questions
    mem.tools_used.append("intake")
    state.update({"memory": mem.model_dump(), "action": "ask_clarifying", "result": {"clarifying_questions": questions}})
    return state


def node_decide(state: HRState) -> str:
    mem = Memory(**state.get("memory", {}))
    have_roles = len(mem.roles_needed) > 0
    have_skills = bool(mem.constraints.get("skills"))
    have_budget = bool(mem.constraints.get("budget"))
    if have_roles and have_skills and have_budget:
        return "draft_jds"
    return "ask_more"

def node_ask_more(state: HRState) -> HRState:
    mem = Memory(**state.get("memory", {}))
    mem.tools_used.append("ask_more")
    state.update({"memory": mem.model_dump(), "result": {"clarifying_questions": mem.clarifying_questions}})
    return state


def node_draft_jds(state: HRState) -> HRState:
    mem = Memory(**state.get("memory", {}))
    jds = [draft_job_description(role, mem.constraints) for role in mem.roles_needed]
    mem.job_descriptions = jds
    mem.tools_used.append("jd_drafter")
    state.update({"memory": mem.model_dump(), "action": "build_plan", "result": {"job_descriptions": jds}})
    return state


def node_build_plan(state: HRState) -> HRState:
    mem = Memory(**state.get("memory", {}))
    plan = tool_checklist_builder(mem.roles_needed, mem.constraints)
    mem.hiring_plan = plan
    mem.tools_used.append("plan_builder")
    state.update({"memory": mem.model_dump(), "action": "complete", "result": {"hiring_plan": plan}})
    return state
