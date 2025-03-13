from app.tool.search.base import WebSearchEngine
from googlesearch import search

class GoogleSearchEngine(WebSearchEngine):
    
    def perform_search(self, query, num_results = 10, *args, **kwargs):
        """Google search engine."""
        return search(query, num_results=num_results)
