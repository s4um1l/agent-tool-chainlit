import os
import sys
import chainlit as cl
from src.research_agent import run_agent, create_system_message
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

# Set domain as global variable
DOMAIN = "General Research"
DEBUG_MODE = True  # Set to True to show detailed tool usage

# List of available domains
AVAILABLE_DOMAINS = [
    "General Research",
    "Computer Science",
    "Medicine",
    "Finance",
    "Climate Science",
    "Artificial Intelligence",
    "History",
    "Psychology",
    "Physics",
    "Biology"
]

@cl.on_chat_start
async def on_chat_start():
    """
    Initialize the chat session
    """
    # Set up the session state
    cl.user_session.set("messages", [create_system_message(DOMAIN)])
    cl.user_session.set("debug_mode", DEBUG_MODE)
    
    # Send a welcome message
    await cl.Message(
        content=f"Hello! I'm your research assistant specialized in {DOMAIN}. How can I help you?\n\n"
                f"I have access to the following tools:\n"
                f"1. 🔎 Web Search - For recent information and general queries\n"
                f"2. 📄 Research Papers - For academic and scientific knowledge\n"
                f"3. 📚 Wikipedia - For background information and factual summaries\n"
                f"4. 📊 Data Analysis - For analyzing data you provide\n\n"
                f"You can change the research domain by typing `/domain` followed by one of these options:\n"
                f"{', '.join(AVAILABLE_DOMAINS)}\n\n"
                f"You can toggle debug mode with `/debug on` or `/debug off` to see detailed tool usage.",
        author="Research Assistant"
    ).send()

@cl.on_settings_update
async def on_settings_update(settings):
    """
    Handle settings updates
    """
    global DOMAIN
    
    if "domain" in settings:
        DOMAIN = settings["domain"]
        # Reset messages with new domain
        cl.user_session.set("messages", [create_system_message(DOMAIN)])
        
        # Notify user of domain change
        await cl.Message(
            content=f"Domain changed to {DOMAIN}. My knowledge is now specialized for this domain.",
            author="System"
        ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Process incoming messages
    """
    global DOMAIN, DEBUG_MODE
    
    # Check for debug mode command
    if message.content.startswith("/debug"):
        command_parts = message.content.split()
        if len(command_parts) > 1:
            if command_parts[1].lower() == "on":
                DEBUG_MODE = True
                cl.user_session.set("debug_mode", True)
                await cl.Message(
                    content="Debug mode turned ON. You'll see detailed tool usage information.",
                    author="System"
                ).send()
            elif command_parts[1].lower() == "off":
                DEBUG_MODE = False
                cl.user_session.set("debug_mode", False)
                await cl.Message(
                    content="Debug mode turned OFF.",
                    author="System"
                ).send()
        else:
            current_state = "ON" if DEBUG_MODE else "OFF"
            await cl.Message(
                content=f"Debug mode is currently {current_state}. Use `/debug on` or `/debug off` to change.",
                author="System"
            ).send()
        return
    
    # Check for domain change command
    if message.content.startswith("/domain"):
        command_parts = message.content.split()
        if len(command_parts) == 1:
            # Display available domains
            domains_list = "\n".join([f"- {domain}" for domain in AVAILABLE_DOMAINS])
            await cl.Message(
                content=f"Please specify a domain. Available domains:\n{domains_list}\n\nExample: `/domain Artificial Intelligence`",
                author="System"
            ).send()
            return
        
        # Get the requested domain
        requested_domain = " ".join(command_parts[1:])
        
        # Check if it's in the available domains (case insensitive)
        found_domain = None
        for domain in AVAILABLE_DOMAINS:
            if domain.lower() == requested_domain.lower():
                found_domain = domain
                break
        
        if found_domain:
            DOMAIN = found_domain
            # Reset messages with new domain
            cl.user_session.set("messages", [create_system_message(DOMAIN)])
            
            # Notify user of domain change
            await cl.Message(
                content=f"Domain changed to {DOMAIN}. My knowledge is now specialized for this domain.",
                author="Research Assistant"
            ).send()
        else:
            # Domain not found
            domains_list = "\n".join([f"- {domain}" for domain in AVAILABLE_DOMAINS])
            await cl.Message(
                content=f"Domain '{requested_domain}' not found. Available domains:\n{domains_list}",
                author="System"
            ).send()
        return
    
    # Get current message history and debug mode setting
    messages = cl.user_session.get("messages")
    debug_mode = cl.user_session.get("debug_mode", DEBUG_MODE)
    
    # Add user message to history
    user_message = HumanMessage(content=message.content)
    
    # Create a temporary thinking message
    thinking = cl.Message(content="Researching your query...", author="Research Assistant")
    await thinking.send()
    
    try:
        # Call the agent
        response_messages = run_agent(
            user_input=message.content,
            domain=DOMAIN,
            messages=messages
        )
        
        # Update the thinking message
        await thinking.remove()
        
        # Track tool usage for summary
        tool_usage = []
        
        # Process and display messages
        for msg in response_messages:
            if not msg in messages:  # Only process new messages
                if isinstance(msg, AIMessage):
                    await cl.Message(
                        content=msg.content,
                        author="Research Assistant"
                    ).send()
                elif isinstance(msg, ToolMessage):
                    # Add to tool usage list
                    tool_usage.append(msg.name)
                    
                    # Create elements for tool output
                    elements = []
                    
                    # Format the tool output for better readability
                    formatted_content = msg.content
                    # Try to detect JSON and format it
                    if msg.content.strip().startswith('{') or msg.content.strip().startswith('['):
                        try:
                            import json
                            content_obj = json.loads(msg.content)
                            formatted_content = json.dumps(content_obj, indent=2)
                        except:
                            pass
                    
                    # Add tool output as an element
                    elements.append(
                        cl.Text(
                            name=f"Tool Result: {msg.name}",
                            content=formatted_content,
                            display="inline"
                        )
                    )
                    
                    # Only show detailed tool messages in debug mode
                    if debug_mode:
                        # Send tool message with more prominent styling
                        await cl.Message(
                            content=f"🔍 **TOOL CALL**: `{msg.name}`\n\nI used this tool to find information about your query.",
                            author="Research Assistant",
                            elements=elements
                        ).send()
        
        # Display tool usage summary if tools were used
        if tool_usage and debug_mode:
            tool_counts = {}
            for tool in tool_usage:
                if tool in tool_counts:
                    tool_counts[tool] += 1
                else:
                    tool_counts[tool] = 1
            
            summary = "📊 **RESEARCH SUMMARY**\n\nTo answer your question, I used:\n"
            for tool, count in tool_counts.items():
                # Add emoji based on tool type
                emoji = "🔎" if tool == "web_search" else "📄" if tool == "research_paper_search" else "📚" if tool == "wikipedia_search" else "📊"
                summary += f"- {emoji} `{tool}`: {count} time{'s' if count > 1 else ''}\n"
            
            await cl.Message(
                content=summary,
                author="System"
            ).send()
        
        # Update session with new messages
        cl.user_session.set("messages", response_messages)
        
    except Exception as e:
        await thinking.remove()
        await cl.Message(
            content=f"Sorry, I encountered an error: {str(e)}",
            author="System"
        ).send() 