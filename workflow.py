from langgraph.graph import StateGraph, END
from nodes import HRState, node_intake, node_decide, node_ask_more, node_draft_jds, node_build_plan

workflow = StateGraph(HRState)
workflow.add_node("intake", node_intake)
workflow.add_node("ask_more", node_ask_more)
workflow.add_node("draft_jds", node_draft_jds)
workflow.add_node("build_plan", node_build_plan)

workflow.set_entry_point("intake")
workflow.add_conditional_edges(
    "intake",
    node_decide,
    {"ask_more": "ask_more", "draft_jds": "draft_jds"}
)
workflow.add_edge("ask_more", END)
workflow.add_edge("draft_jds", "build_plan")
workflow.add_edge("build_plan", END)


app_graph = workflow.compile()
