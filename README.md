# Agentic HR Hiring Planner (LangGraph)

This project is a modular **Agentic AI application** built with [LangGraph](https://github.com/langchain-ai/langgraph).  
It helps HR professionals design a hiring process by asking clarifying questions, drafting job descriptions, and building a structured hiring plan.

Steps to run this code

1. Clone this repository or copy the code into a folder called `SquareShift`.
2. Install dependencies (Python 3.9+ recommended):
  ```bash
  pip install langgraph pydantic
  ```
3. If you plan to replace template logic with real LLM calls Install
 `pip install openai`


Run the app 
```bash
python main.py --session `session_name`
```
Default session name is `default`. 

Potential output:
```json
{
  "user_input": "I need to hire a founding engineer and a GenAI intern. Can you help?",
  "memory": {
    "roles_needed": ["Founding Engineer", "GenAI Intern"],
    "constraints": {},
    "clarifying_questions": [
      "What is your total budget per role (base + equity)? If unsure, give a range.",
      "What seniority level(s) are you targeting (e.g., founding/staff vs. intern/junior)?",
      "What must-have technical/functional skills should candidates have?",
      "What is your ideal time-to-fill in weeks?",
      "Are these roles remote, hybrid, or onsite? If onsite, where?",
      "Any interview process preferences (take-home vs live, panel size)?"
    ],
    "job_descriptions": [],
    "hiring_plan": {},
    "tools_used": ["intake"]
  },
  "action": "ask_clarifying",
  "result": {
    "clarifying_questions": [...]
  }
}
```


