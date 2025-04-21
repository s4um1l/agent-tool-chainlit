# Research Assistant Agent

This application is a research assistant powered by LangGraph and LangChain. It can help you find information on various topics using three specialized tools:

## Available Tools

1. **Web Search**: For general queries and recent information
2. **Research Paper Search**: For academic and scientific research papers
3. **Data Analysis**: For analyzing data sets you provide in JSON or CSV format

## How to Use

1. Choose your research domain in the settings panel
2. Ask any question related to your chosen domain
3. The agent will use the appropriate tools to research and answer your question

## Example Queries

- "What are the latest developments in quantum computing?"
- "Find research papers about climate change impacts on agriculture"
- "Analyze this data: [paste JSON or CSV]"

## Tips

- Be specific in your questions for better results
- For data analysis, make sure your data is properly formatted
- Change the domain setting to get more specialized answers for your topic

---
settings:
  - name: domain
    title: Research Domain
    description: Specialized domain for the research assistant
    type: select
    default: General Research
    options:
      - General Research
      - Computer Science
      - Medicine
      - Finance
      - Climate Science
      - Artificial Intelligence
      - History
      - Psychology
      - Physics
      - Biology 