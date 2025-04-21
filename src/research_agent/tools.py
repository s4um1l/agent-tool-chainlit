from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain.tools import BaseTool
from typing import Optional, Type, Any, List, Dict
from pydantic import BaseModel, Field
import json
import pandas as pd
import requests

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for general information and current events. Use this for queries about recent developments or general topics."
    
    def _run(self, query: str) -> str:
        tavily_tool = TavilySearchResults(max_results=3)
        results = tavily_tool.invoke(query)
        return json.dumps(results, indent=2)

class ResearchPaperTool(BaseTool):
    name: str = "research_paper_search"
    description: str = "Search for academic research papers on a topic. Use this for scientific information and academic knowledge."
    
    def _run(self, query: str) -> str:
        arxiv_tool = ArxivQueryRun()
        results = arxiv_tool.invoke(query)
        return results

class WikipediaSearchTool(BaseTool):
    name: str = "wikipedia_search"
    description: str = "Search Wikipedia for comprehensive background information on a topic. Use this for factual summaries and foundational knowledge."
    
    def _run(self, query: str) -> str:
        wikipedia_tool = WikipediaQueryRun(top_k_results=3)
        results = wikipedia_tool.invoke(query)
        return results

class DataAnalysisInput(BaseModel):
    data: str = Field(..., description="JSON or CSV formatted data to analyze")
    analysis_type: str = Field(..., description="Type of analysis to perform (summary, trends, comparison)")
    
class DataAnalysisTool(BaseTool):
    name: str = "data_analysis"
    description: str = "Analyze data provided in JSON or CSV format. Can perform summary, trends, or comparison analysis."
    args_schema: Type[BaseModel] = DataAnalysisInput
    
    def _run(self, data: str, analysis_type: str) -> str:
        try:
            # Try to parse as JSON
            try:
                parsed_data = json.loads(data)
                df = pd.DataFrame(parsed_data)
            except:
                # Try as CSV
                import io
                df = pd.read_csv(io.StringIO(data))
            
            if analysis_type == "summary":
                return f"Summary Statistics:\n{df.describe().to_string()}"
            elif analysis_type == "trends":
                if len(df.columns) >= 2:
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) >= 2:
                        return f"Correlation Analysis:\n{df[numeric_cols].corr().to_string()}"
                    return "Not enough numeric columns for trend analysis"
                return "Not enough columns for trend analysis"
            elif analysis_type == "comparison":
                return f"Column Comparison:\n{df.head(10).to_string()}"
            else:
                return f"Unknown analysis type: {analysis_type}"
        except Exception as e:
            return f"Error analyzing data: {str(e)}"

def get_tools():
    return [
        WebSearchTool(),
        ResearchPaperTool(),
        WikipediaSearchTool(),
        DataAnalysisTool()
    ] 