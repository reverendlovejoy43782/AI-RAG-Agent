import os
import wikipedia
from langchain.tools import tool
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
        max_results=5,  # You can configure this based on your needs
        search_depth="advanced",  # Options are "basic" or "advanced"
        include_domains=[],  # Add specific domains to include
        exclude_domains=[],  # Add specific domains to exclude
        include_answer=False,  # Set to True to include a short answer in the results
        include_raw_content=False,  # Set to True to include raw HTML content
        include_images=False  # Set to True to include images in the results
    )
    results = tavily.invoke(query)
    if not results:
        return "No results found"
    
    # Return the most relevant content or title and URL
    formatted_results = []
    for result in results[:3]:
        title = result.get("title", "No title")
        url = result.get("url", "No URL")
        content = result.get("content", "No content available")
        formatted_results.append(f"Title: {title}\nURL: {url}\nContent: {content}")

    return "\n\n".join(formatted_results)

tools = [search_wikipedia, search_tavily]



"""
import os
import wikipedia
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

@tool
def search_wikipedia(query: str) -> str:
    #Run Wikipedia search and get page summaries.
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
    #Run Tavily search and get results.
    api_key = os.getenv('TAVILY_API_KEY')
    tavily = TavilySearchResults(
        api_key=api_key,
        max_results=5,  # You can configure this based on your needs
        search_depth="advanced",  # Options are "basic" or "advanced"
        include_domains=[],  # Add specific domains to include
        exclude_domains=[],  # Add specific domains to exclude
        include_answer=False,  # Set to True to include a short answer in the results
        include_raw_content=False,  # Set to True to include raw HTML content
        include_images=False  # Set to True to include images in the results
    )
    results = tavily.invoke(query)
    if not results:
        return "No results found"
    # Return the most relevant content or title and URL
    formatted_results = []
    for result in results[:3]:
        title = result.get("title", "No title")
        url = result.get("url", "No URL")
        content = result.get("content", "No content available")
        formatted_results.append(f"Title: {title}\nContent: {content}")

    return "\n\n".join(formatted_results)

tools = [search_wikipedia, search_tavily]
"""