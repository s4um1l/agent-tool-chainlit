import os
from typing import Dict, TypedDict, List, Annotated, Literal, Union, Any
from .tools import get_tools
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
import operator
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    FunctionMessage,
)
from langchain_core.tools import BaseTool, tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import json

# State definition
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize tools
tools = get_tools()

# System prompt
system_prompt = """You are an AI research assistant specialized in {domain}.
Your goal is to help users find accurate information about {domain} topics.

You have access to the following tools:
1. Web Search - For general queries and recent information
2. Research Paper Search - For academic and scientific information
3. Wikipedia Search - For comprehensive background information and factual summaries
4. Data Analysis - For analyzing data provided by the user

Choose the most appropriate tool(s) based on the user's question:
- Use Web Search for current events, recent developments, or general information
- Use Research Paper Search for academic knowledge, scientific findings, or technical details
- Use Wikipedia Search for conceptual explanations, definitions, historical context, or general facts
- Use Data Analysis when the user provides data to be analyzed

Always try to provide the most accurate and helpful information.
When responding, cite your sources appropriately."""

# Function to create the system message
def create_system_message(domain):
    return SystemMessage(content=system_prompt.format(domain=domain))

# Create the graph
def create_agent_graph(domain="general research"):
    """
    Create a LangGraph for the research agent using prebuilt components
    """
    # Initialize the graph with the state
    workflow = StateGraph(AgentState)
    
    # Add system message with domain context
    system_prompt_message = create_system_message(domain)
    
    # Agent node function
    def agent_node(state: AgentState):
        messages = state["messages"]
        if len(messages) == 0 or not isinstance(messages[0], SystemMessage):
            messages = [system_prompt_message] + messages
        
        # Create model and bind tools
        model = ChatOpenAI(model="gpt-4o", temperature=0)
        model_with_tools = model.bind_tools(tools)
        
        # Generate response with tools
        return {"messages": [model_with_tools.invoke(messages)]}
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    
    # Use prebuilt ToolNode
    tool_node = ToolNode(tools=tools)
    workflow.add_node("tools", tool_node)
    
    # Add conditional edges using prebuilt tools_condition
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Add edge back to agent after tools execution
    workflow.add_edge("tools", "agent")
    
    # Set the entry point
    workflow.add_edge(START, "agent")
    
    # Compile the graph
    return workflow.compile()

# Function to run the agent
def run_agent(user_input, domain="general research", messages=None):
    """
    Run the agent with a user input
    """
    # Create the graph
    graph = create_agent_graph(domain)
    
    # Initialize messages if not provided
    if messages is None:
        messages = [HumanMessage(content=user_input)]
    else:
        messages.append(HumanMessage(content=user_input))
    
    # Run the graph
    result = graph.invoke({"messages": messages})
    
    return result["messages"]

if __name__ == "__main__":
    # Test the agent
    domain = "artificial intelligence"
    query = "What are the latest developments in natural language processing?"
    
    messages = run_agent(query, domain)
    for message in messages:
        if isinstance(message, AIMessage):
            print("AI:", message.content)
        elif isinstance(message, HumanMessage):
            print("Human:", message.content)
        elif isinstance(message, ToolMessage):
            print(f"Tool ({message.name}):", message.content[:100] + "..." if len(message.content) > 100 else message.content) 