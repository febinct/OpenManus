try:
    from baidusearch.baidusearch import search
    BAIDUSEARCH_AVAILABLE = True
except ImportError:
    BAIDUSEARCH_AVAILABLE = False

from app.tool.search.base import WebSearchEngine


class BaiduSearchEngine(WebSearchEngine):
    
    def perform_search(self, query, num_results = 10, *args, **kwargs):
        """Baidu search engine."""
        if not BAIDUSEARCH_AVAILABLE:
            return [{"title": "BaiduSearch module not available", 
                    "link": "", 
                    "snippet": "Please install the baidusearch package in your virtual environment with 'pip install baidusearch'"}]
        
        return search(query, num_results=num_results)
