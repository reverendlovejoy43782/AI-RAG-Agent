import os
import wikipedia
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@tool
def search_wikipedia(query: str) -> str:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query)
    summaries = []
    for page_title in page_titles[:3]:
        try:
            wiki_page = wikipedia.page(title=page_title, auto_suggest=False)
            summaries.append(f"Page: {page_title}\nSummary: {wiki_page.summary}")
        except wikipedia.exceptions.PageError:
            pass
        except wikipedia.exceptions.DisambiguationError:
            pass
    if not summaries:
        return "No good Wikipedia Search Result was found"
    return "\n\n".join(summaries)





@tool
def search_tavily(query: str) -> str:
    """Run Tavily search and get results."""
    api_key = os.getenv('TAVILY_API_KEY')
    tavily = TavilySearchResults(
        api_key=api_key,
        #max_results=5,
        search_depth="advanced",
        include_domains=[],
        exclude_domains=[], 
        include_answer=True,
        include_raw_content=False,
        include_images=False
    )
    results = tavily.invoke(query)
    if not results:
        return "No results found"
    
    formatted_results = []
    for result in results[:5]:
        url = result.get("url", "No URL")
        content = result.get("content", "No content available")
        formatted_results.append(f"URL: {url}\nContent: {content}")

    return "\n\n".join(formatted_results)



tools = [search_wikipedia, search_tavily]