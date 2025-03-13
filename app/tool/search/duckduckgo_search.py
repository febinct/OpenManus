try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

from app.tool.search.base import WebSearchEngine


class DuckDuckGoSearchEngine(WebSearchEngine):
    
    def perform_search(self, query, num_results = 10, *args, **kwargs):
        """DuckDuckGo search engine."""
        if not DUCKDUCKGO_AVAILABLE:
            return [{"title": "DuckDuckGo Search module not available", 
                    "link": "", 
                    "snippet": "Please install the duckduckgo_search package in your virtual environment with 'pip install duckduckgo_search'"}]
        
        return DDGS().text(query, max_results=num_results)
