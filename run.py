import os
import sys
from src.research_agent import run_agent
from langchain_core.messages import AIMessage, ToolMessage

def main():
    """
    Run the research agent from the command line
    """
    # Check if domain is provided
    if len(sys.argv) >= 2:
        domain = sys.argv[1]
    else:
        domain = "General Research"
        print(f"No domain specified, using default: {domain}")
    
    print(f"\n=== Research Assistant ({domain}) ===\n")
    print("Ask your question or type 'exit' to quit.\n")
    
    # Main interaction loop
    messages = None
    while True:
        # Get user input
        user_input = input("> ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nGoodbye!")
            break

        try:    
            # Run the agent
            print("\nResearching...\n")
            messages = run_agent(user_input, domain, messages)
            
            # Print AI response
            for message in messages[-3:]:  # Print only the last few messages
                if hasattr(message, "type") and message.type == "ai":
                    print(f"\nAssistant: {message.content}\n")
                elif hasattr(message, "type") and message.type == "tool" and hasattr(message, "name"):
                    print(f"\n[Tool: {message.name}]\n{message.content[:200]}...\n" 
                          if len(message.content) > 200 else f"\n[Tool: {message.name}]\n{message.content}\n")
                elif hasattr(message, "content"):
                    if isinstance(message, AIMessage):
                        print(f"\nAssistant: {message.content}\n")
                    elif isinstance(message, ToolMessage) and hasattr(message, "name"):
                        print(f"\n[Tool: {message.name}]\n{message.content[:200]}...\n" 
                              if len(message.content) > 200 else f"\n[Tool: {message.name}]\n{message.content}\n")
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            print("Let's try again with a different question.")

if __name__ == "__main__":
    # Check for environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
            
        if not os.environ.get("OPENAI_API_KEY"):
            api_key = input("Enter your OpenAI API key: ")
            os.environ["OPENAI_API_KEY"] = api_key
    
    if not os.environ.get("TAVILY_API_KEY"):
        if os.path.exists(".env"):
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
                
        if not os.environ.get("TAVILY_API_KEY"):
            api_key = input("Enter your Tavily API key: ")
            os.environ["TAVILY_API_KEY"] = api_key
    
    main() 