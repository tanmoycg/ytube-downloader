import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from youtubesearchpython import VideosSearch
#from pydub import AudioSegment
import yt_dlp
from pathlib import Path
import time
import shutil

MY_FILE_OF_SONGS = "Songs_To_Be_Downloaded.txt"
MY_DOWNLOAD_DIRECTORY = "downloads"
MY_NUM_FNAME_COMPONENTS = 6


def main():
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

def cleanup_create(directory):
    directory_path = os.path.join(Path.cwd(), directory)
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)
            print(f"Removed existing directory: {directory_path}")
            # Wait to ensure complete deletion
            time.sleep(1)  
        except Exception as e:
            print(f"Cleanup failed: {e}")
            raise  # Stop execution if cleanup fails
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Created fresh directory: {directory_path}")
    except Exception as e:
        print(f"Directory creation failed: {e}")
        raise   
       
def read_nameof_songs(textfile_song_names):
    """Read name of cotent (video/audio) from text file.
    
    Read name of content from text file. The text file is assumed  
    to be in the current working directory. The entires are in in 
    the format "a contentname" or "v contentname". Either video or 
    audio will be downloaded depending on "v" or "a" respectively.

    Args: 
        textfile_song_names: Name of the text file
    
    Returns: A list of dicts holding the name and type of content. 
    """
    entries = []
    with open(textfile_song_names) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Split into type (first char) and query (rest of line)
            content_type, query = line[0], line[1:].strip()
            if content_type not in ('a', 'v'):
                print(f"Invalid type '{content_type}' for query: '{query}'. Skipping.")
                continue
            entries.append({'type': content_type, 'query': query})
    return entries

def search_youtube(query, max_results=1):
    """Gets YouTube URL corresponsing to a query(song name)
    
    Searches YouTube to get URL of a song through module 
    "youtubesearchpython". Function "VideosSearch" from this 
    module is used

    Args: 
        query (string): Name of song.
        max_results (int) : No. of results to be returned. 
    
    Returns: URL of the song or "None" if not found
    """
    videos_search = VideosSearch(query, limit=max_results)
    results = videos_search.result()
    
    if results['result']:
        return results['result'][0]['link']  # Return the first result's URL
    else:
        return None

def get_all_youtube_urls(queries):
    """Gets all YouTube URL's corresponsing to queries
    
    Uses ThreadPoolEcecutor to invoke function "search_youtube" for getting URL's. 
    The function "search_youtube" returns URL of a single song/video.
    
    Args: 
        queries (list of dict(s)): [{type, query}, ......]
            
    Returns: URL(s), type(v/a) of the entry(s) or empty list if no urls are found.
    v: video, a: audio
    """
    entries = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(search_youtube, entry['query']): entry for entry in queries}
        for future in as_completed(futures):
            entry = futures[future]
            try:
                url = future.result()
                if url:
                    entries.append({'type': entry['type'], 'url': url, 'query': entry['query']})
            except Exception as e:
                print(f"Error fetching URL for '{entry['query']}': {e}")
    return entries

def download_all_ytube_urls(ytube_entries):
    """Downloads all URLs with video/audio selection
    
    Uses ThreadPoolEcecutor to invoke appropriate function to download 
    audio/video corresponding to an entry.
    
    Args: 
        ytube_entries (list of dicts): URL, Type of Content 
            
    Returns: Absolute filenames of the downloaded files
    """
    downloaded_files = []
    with ThreadPoolExecutor() as executor:
        futures = {}
        for entry in ytube_entries:
            url = entry['url']
            # Choose downloader based on type
            downloader = (
                download_youtube_video if entry['type'] == 'v' 
                else download_youtube_audio_as_mp3
            )
            futures[executor.submit(downloader, url)] = entry['query']

        for future in as_completed(futures):
            try:
                downloaded_file = future.result()
                if downloaded_file:
                    downloaded_files.append(downloaded_file)
            except Exception as e:
                query = futures[future]
                print(f"Error downloading '{query}': {e}")
    return downloaded_files

def download_youtube_audio_as_mp3(youtube_url, output_path=MY_DOWNLOAD_DIRECTORY):
    """Downloads file corresponsing to an URL.
    
    Uses "Yt_dlp" to download file from YouTube. ffmg should be present in the 
    system. The function "ydl.extract_info" does the actual download. The 
    "info_dict" dictionary holds the download details. The filename is 
    extracted from here. 
        
    Args: 
        ytube_url (string): Name of URL to be downloaded.
        output_path (string): Directory where downloaded file is to be saved.
            
    Returns: Absolute pathname of the downloaded file.
    """
    # Set up options for yt-dlp to download audio only
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Output format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Convert to mp3
            'preferredquality': '192',  # Bitrate
        }],
        'noprogress': True,  # Cleaner output with threads
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],  # Avoid fragmented streams
                'player_client': ['android']  # Most stable
    }
}
    }
    
    # Download the video as audio using yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        # Extract the actual saved file name
        downloads = info_dict.get("requested_downloads", [])
        file_name = downloads[0].get("filepath") if downloads else None
     
    return file_name

def download_youtube_video(youtube_url, output_path=MY_DOWNLOAD_DIRECTORY):
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
        
def shorten_all_downloaded_file_names(download_dir):
    """Converts long filenames in the download directory to shorter names
    
    The downloaded filenames are long. This function gets all the filenames from 
    the directory and calls a function (shorten_downloaded_file_name) to rename the files, so that the filenames 
    are shortended. It uses ThreadPoolEcecutor to invoke function. Absolute path names
    of the files are passed to "shorten_downloaded_file_name"
        
    Args: 
        download_dir (string): The directory where downloaded songs are saved.
                    
    Returns: Shortended file names.
    """
    short_file_names = []
    directory = os.path.join(Path.cwd(), download_dir)
    all_files = [entry.name for entry in os.scandir(directory) if entry.is_file()]
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(shorten_downloaded_file_name, 
                    os.path.join(directory, myfile)): myfile for myfile in all_files}
        for future in as_completed(futures):
            try:
                short_file_name = future.result()
                if short_file_name:
                    short_file_names.append(short_file_name)
            except Exception as e:
                myfile = futures[future]  # Look up the filename that caused the error
                print(f"Error Renaming File for '{myfile}': {e}")
    return short_file_names

def shorten_downloaded_file_name(abs_path_out_file):
    try:    
        folder, filename = os.path.split(abs_path_out_file)
        name, ext = os.path.splitext(filename)
        short_name = return_short_string(MY_NUM_FNAME_COMPONENTS, name)
        new_path = os.path.join(folder, f"{short_name}{ext}")  # Preserve original extension
        
        # Ensure no overwrite
        if os.path.exists(new_path):
            base, counter = new_path, 1
            while os.path.exists(new_path):
                new_path = f"{base}_{counter}{ext}"
                counter += 1
                
        os.rename(abs_path_out_file, new_path)
        return os.path.basename(new_path)
    except Exception as e:
        print(f"Error renaming {abs_path_out_file}: {e}")
        return None
    
def return_short_string(num_of_words, mystr):
  """Restricts the number of words in a string to "num_of_words"

    Args: 
        num_of_words (int): Restriction on number of words.
        mystr (string): The input string. 
                    
    Returns: Shortended string having at max "num_of_words" words
    """
  word_list = mystr.split()
  if len(word_list) >= num_of_words:
       return "_".join(word_list[0:num_of_words])
  else:
       return "_".join(word_list)

def measure_time(func, *args, **kwargs):
    
    start_time = time.time()  # Start the timer
    result = func(*args, **kwargs)  # Call the function with any arguments
    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    
    print(f"Execution time: {elapsed_time:.6f} seconds")
    return result

if __name__ == "__main__":
    measure_time(main)
