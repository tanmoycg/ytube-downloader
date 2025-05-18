from typing import Dict, List, Optional
from youtubesearchpython import VideosSearch
from concurrent.futures import ThreadPoolExecutor, as_completed

def search_youtube(query: str, max_results: int = 1) -> Optional[str]:
    """Searches YouTube and returns first video URL."""
    videos_search = VideosSearch(query, limit=max_results)
    results = videos_search.result()
    return results['result'][0]['link'] if results['result'] else None

def get_all_youtube_urls(queries: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Batch-resolves YouTube URLs using threading."""
    entries: List[Dict[str, str]] = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(search_youtube, entry['query']): entry for entry in queries}
        for future in as_completed(futures):
            entry = futures[future]
            try:
                if url := future.result():
                    entries.append({**entry, 'url': url})
            except Exception as e:
                print(f"URL resolution failed for {entry['query']}: {e}")
    return entries