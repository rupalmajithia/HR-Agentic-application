import json
import argparse
from pathlib import Path
from memory import Memory
from workflow import app_graph
from llm_helpers import parse_roles_from_text

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

def session_file(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"

def load_session(session_id: str) -> Memory:
    f = session_file(session_id)
    if f.exists():
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        return Memory(**data["memory"])
    return Memory()

def save_session(session_id: str, mem: Memory, result: dict):
    f = session_file(session_id)
    payload = {"memory": mem.model_dump(), "result": result}
    with open(f, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False)

def parse_answer(question: str, answer: str):
    q = question.lower()
    a = answer.strip()
    if "remote" in q or "location" in q:
        return ("location", a)
    if "roles" in q:
        return ("roles", [r.strip() for r in a.split(",") if r.strip()])
    if "budget" in q:
        return ("budget", a)
    if "seniority" in q:
        return ("seniority", a)
    if "skills" in q:
        return ("skills", [s.strip() for s in a.split(",") if s.strip()])
    if "time" in q or "week" in q:
        digits = "".join(ch for ch in a if ch.isdigit())
        return ("timeline_weeks", int(digits)) if digits else ("timeline_weeks", a)
    if "process" in q:
        return ("process_prefs", a)
    return (None, a)

def print_final_response(mem: Memory, result: dict, session_id: str):
    print("\n================ FINAL RESPONSE ================")
    if mem.job_descriptions:
        print("\n=== Job Descriptions ===")
        print(json.dumps(mem.job_descriptions, indent=2, ensure_ascii=False))
    if mem.hiring_plan:
        print("\n=== Hiring Plan ===")
        print(json.dumps(mem.hiring_plan, indent=2, ensure_ascii=False))
    if not mem.job_descriptions and not mem.hiring_plan:
        print("\n(Partial state only — no JD or plan yet)")
        print(json.dumps(mem.model_dump(), indent=2, ensure_ascii=False))
    print("================================================")
    print(f"\nSession '{session_id}' completed and saved.")

def interactive_loop(session_id: str):
    mem = load_session(session_id)

    if not mem.roles_needed and not mem.constraints:
        # Probably use an llm model to imporve and verify this response
        init = input("Initial prompt (e.g. 'I need to hire a founding engineer and a GenAI intern'): ").strip()
        if not init:
            init = "I need to hire a founding engineer and a GenAI intern. Can you help?"
        user_input = init
        auto_roles = parse_roles_from_text(init)
        if auto_roles:
            print(f"\nI detected these roles: {auto_roles}")
            confirm = input("Press Enter to confirm, or type corrected roles (comma-separated): ").strip()
            if confirm:
                mem.roles_needed = [r.strip() for r in confirm.split(",") if r.strip()]
            else:
                mem.roles_needed = auto_roles
    else:
        print(f"Loaded session '{session_id}' with memory.")
        user_input = ""

    while True:
        state = {
            "user_input": user_input,
            "memory": mem.model_dump(),
            "action": "",
            "result": {},
        }
        out = app_graph.invoke(state)
        action = out.get("action")
        result = out.get("result", {})
        mem = Memory(**out["memory"])

        # Clarifying questions can be better using the LLM models
        clar_qs = result.get("clarifying_questions") or mem.clarifying_questions
        if clar_qs:
            for q in clar_qs:
                ans = input(f"{q}\n> ").strip()
                if ans.lower() in {"quit", "exit"}:
                    save_session(session_id, mem, result)
                    print_final_response(mem, result, session_id)
                    return
                if ans.lower() == "done":
                    clar_qs = []  # stop early
                    break
                if ans.lower() == "skip" or ans == "":
                    continue
                key, val = parse_answer(q, ans)
                if key == "roles":
                    mem.roles_needed = list(dict.fromkeys(mem.roles_needed + val))
                elif key:
                    mem.constraints[key] = val
                else:
                    mem.constraints.setdefault("notes", []).append({q: val})

            user_input = ""
            save_session(session_id, mem, result)

            if mem.roles_needed and mem.constraints:
                out = app_graph.invoke({
                    "user_input": "",
                    "memory": mem.model_dump(),
                    "action": "",
                    "result": {},
                })
                mem = Memory(**out["memory"])
                result = out.get("result", {})
                action = out.get("action")

        if action == "complete" or mem.hiring_plan or mem.job_descriptions:
            save_session(session_id, mem, result)
            print_final_response(mem, result, session_id)
            return

        # fallback if agent didn't ask questions
        add = input("Add a manual constraint? (y/N): ").strip().lower()
        if add == "y":
            key = input("Constraint key (budget/skills/timeline_weeks/location/process_prefs): ").strip()
            val = input("Value: ").strip()
            if key == "timeline_weeks":
                try:
                    val = int(val)
                except:
                    pass
            elif key == "skills":
                val = [s.strip() for s in val.split(",") if s.strip()]
            mem.constraints[key] = val
            user_input = ""
            save_session(session_id, mem, result)
            continue
        else:
            save_session(session_id, mem, result)
            print_final_response(mem, result, session_id)
            return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic HR Hiring Planner CLI with sessions")
    parser.add_argument("--session", type=str, default="default", help="Session ID")
    args = parser.parse_args()

    interactive_loop(args.session)
