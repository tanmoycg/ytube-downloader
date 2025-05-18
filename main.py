import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from typing import List, Dict
from core.url_resolver import get_all_youtube_urls
from core.downloader import download_all_ytube_urls
from utils.get_user_input import read_nameof_songs
from utils.clean_create_download_dir import cleanup_create
from utils.file_processor import shorten_all_downloaded_file_names
from config import MY_FILE_OF_SONGS, MY_DOWNLOAD_DIRECTORY
import time

def main() -> int:
    """Main execution function."""
    try:
        entries = read_nameof_songs(MY_FILE_OF_SONGS)
        print(f"Found {len(entries)} entries to process")
        
        cleanup_create(MY_DOWNLOAD_DIRECTORY)
        
        url_entries = get_all_youtube_urls(entries)
        print(f"Resolved {len(url_entries)} URLs")
        
        downloaded_files = download_all_ytube_urls(url_entries)
        print(f"Successfully downloaded {len(downloaded_files)} files")
        
        short_names = shorten_all_downloaded_file_names(MY_DOWNLOAD_DIRECTORY)
        print(f"Renamed {len(short_names)} files")
        
        return 0
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    start_time = time.time()
    exit_code = main()
    print(f"Execution time: {time.time() - start_time:.2f} seconds")
    exit(exit_code)