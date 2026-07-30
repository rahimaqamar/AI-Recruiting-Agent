# This file connects all of the nodes 
# you've already created into a LangGraph workflow.

"""
LangGraph Workflow

Connects all Week 3 agent nodes.
"""
# stategraph: create a workflow graph
# start: beginning of workflow
# end: end of workflow

from langgraph.graph import StateGraph, START, END

from app.agent.agent_state import AgentState

from app.agent.planner import planner_node
from app.agent.search import search_node
from app.agent.evaluator import evaluator_node
from app.agent.summary import summary_node
from app.agent.interview import interview_node
from app.agent.improve_job import improve_job_node
from app.agent.self_checker import self_checker_node
from app.agent.reporter import reporter_node


# ==========================================
# Create Graph
# ==========================================

graph = StateGraph(AgentState)


# ==========================================
# Add Nodes
# ==========================================

graph.add_node("planner", planner_node)

graph.add_node("search", search_node)

graph.add_node("evaluator", evaluator_node)

graph.add_node("summary", summary_node)

graph.add_node("interview", interview_node)

graph.add_node("improve_job", improve_job_node)

graph.add_node("self_checker", self_checker_node)

graph.add_node("reporter", reporter_node)


# ==========================================
# Connect Nodes
# ==========================================

graph.add_edge(START, "planner")

graph.add_edge("planner", "search")

graph.add_edge("search", "evaluator")

graph.add_edge("evaluator", "summary")

graph.add_edge("summary", "interview")

graph.add_edge("interview", "improve_job")

graph.add_edge("improve_job", "self_checker")

graph.add_edge("self_checker", "reporter")

graph.add_edge("reporter", END)


# ==========================================
# Compile Graph
# ==========================================

agent_graph = graph.compile()