# Research Agent with LangGraph

This project implements a research agent using LangGraph and LangChain. The agent is capable of researching any domain using three powerful tools and can be deployed with a Chainlit frontend.

## Features

- Domain-specific research assistant
- Three specialized research tools:
  1. Web Search - For general queries and recent information
  2. Research Paper Search - For academic papers and scientific information
  3. Data Analysis - For analyzing data provided by the user
- Interactive Chainlit web interface
- Configurable research domain

## Architecture

This project uses:
- **LangGraph**: For creating the agent's workflow graph with cyclic behavior
- **LangChain**: For tool integration and language model interactions
- **Chainlit**: For the web-based frontend
- **OpenAI GPT-4o**: As the underlying language model

## Installation

1. Clone this repository
2. Install dependencies using UV (recommended) or pip:

```bash
# Using UV
uv pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with the following content:

```
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Usage

To run the application:

```bash
chainlit run app.py -w
```

This will start the Chainlit server and open a web browser with the interface.

## File Structure

- `agent.py`: Contains the LangGraph implementation of the research agent
- `tools.py`: Defines the three research tools
- `app.py`: Chainlit web interface 
- `chainlit.md`: Welcome page content for Chainlit
- `requirements.txt`: Dependencies for the project

## Customization

You can customize the agent by:
1. Modifying the `DOMAIN` variable in `app.py`
2. Adding new tools in `tools.py`
3. Changing the system prompt in `agent.py`

## Example Queries

- "What are the latest developments in quantum computing?"
- "Find research papers about climate change impacts on agriculture"
- "Analyze this data: [paste JSON or CSV]"

## License

MIT 