from langgraph.graph import StateGraph, START, END, MessagesState
from agents import (supervisor_node, order_node, support_node, web_search_node, human_node, validator_node)

# Define the state graph
graph = StateGraph(MessagesState)

# Add nodes to the graph
graph.add_node("supervisor", supervisor_node)
graph.add_node("order", order_node)
graph.add_node("support", support_node)
graph.add_node("web_search_node", web_search_node)
graph.add_node("human_node", human_node)
graph.add_node("validator", validator_node)

# Define the edges and control flow
graph.add_edge(START, "supervisor") # Start with the supervisor


# Compile the graph
app = graph.compile()