import os
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional
from config import MY_DOWNLOAD_DIRECTORY

def download_youtube_audio_as_mp3(youtube_url: str, output_path: str = MY_DOWNLOAD_DIRECTORY) -> Optional[str]:
    """Downloads file corresponding to a YouTube URL and converts to MP3."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noprogress': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_client': ['android']
            }
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        downloads = info_dict.get("requested_downloads", [])
        return downloads[0].get("filepath") if downloads else None

def download_youtube_video(youtube_url: str, output_path: str = MY_DOWNLOAD_DIRECTORY) -> Optional[str]:
    """Robust video downloader with fallback formats"""
    ydl_opts = {
        # Primary format selection (MP4)
        'format': '(bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a])/best[ext=mp4]/best',
        
        # Fallback options
        'format_sort': ['res:1080', 'ext:mp4'],  # Prefer 1080p MP4
        'allow_multiple_video_streams': True,
        'allow_multiple_audio_streams': True,
        
        # Network settings
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': False,
        
        # Output
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': False,
        
        # Bypass restrictions
        'extractor_args': {
            'youtube': {
                'player_skip': ['js'],
                'player_client': ['android', 'web']
            }
        },
        
        # External downloader
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '8', '-k', '1M']
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First try with standard options
            try:
                info = ydl.extract_info(youtube_url, download=True)
                return info.get('requested_downloads', [{}])[0].get('filepath')
            except yt_dlp.utils.DownloadError as e:
                if "Requested format is not available" in str(e):
                    # Fallback to simpler format
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    info = ydl.extract_info(youtube_url, download=True)
                    return info.get('requested_downloads', [{}])[0].get('filepath')
                raise
    except Exception as e:
        print(f"Video download failed for {youtube_url}: {str(e)}")
        return None

def download_all_ytube_urls(ytube_entries: List[Dict[str, str]]) -> List[str]:
    """Downloads all URLs with video/audio selection."""
    downloaded_files: List[str] = []
    with ThreadPoolExecutor() as executor:
        futures = {}
        for entry in ytube_entries:
            url = entry['url']
            downloader = (
                download_youtube_video if entry['type'] == 'v' 
                else download_youtube_audio_as_mp3
            )
            futures[executor.submit(downloader, url)] = entry['query']

        for future in as_completed(futures):
            try:
                if downloaded_file := future.result():
                    downloaded_files.append(downloaded_file)
            except Exception as e:
                query = futures[future]
                print(f"Error downloading '{query}': {e}")
    return downloaded_files