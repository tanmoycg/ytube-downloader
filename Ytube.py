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
    """ main function"""
    name_of_songs = read_nameof_songs(MY_FILE_OF_SONGS)
    print(name_of_songs)
    cleanup_create(MY_DOWNLOAD_DIRECTORY)
    url_of_songs = get_all_youtube_urls(name_of_songs)
    downloaded_files = download_all_ytube_urls(url_of_songs)  
    print(downloaded_files)          
    print("All Dowmloading Processed") 
    shortned_file_names = shorten_all_downloaded_file_names(MY_DOWNLOAD_DIRECTORY)  
    print(shortned_file_names)      
    print("Filenames Shortended ...Enjoy!!")
    return 0
 
def cleanup_create(directory):
    """Removes/Creates the download directory. 
    
    Removes the download diretory if it exists along with all files  
    or creates it,  if it does not exists

    Args: 
        directory: Name of the directory inside current directory where 
        downloaded songs will be placed
    
    Returns: Nothing is returned to the caller

    Raises: OSError if error occurs
    """
    directory_path = os.path.join(Path.cwd(), directory)
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' successfully created")       
        except OSError as e:
            print(f"Error: {e}")
    else:
        # Remove the directory and its contents
        try:
            shutil.rmtree(directory_path)
            print(f"Directory '{directory_path}' and all its contents \
                  have been removed.")
        except OSError as e:
            print(f"Error: {e}")
        
       
def read_nameof_songs(textfile_song_names):
    """Read name of song(s) names from text file.
    
    Read name of song(s) names from text file. The text file is assumed  
    to be in the current working directory.

    Args: 
        textfile_song_names: Name of the text file
    
    Returns: A list holding the name of songs as strings
    """
    with open(textfile_song_names) as f:
        my_list = list(f)
        return [x.rstrip() for x in my_list]

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
    """Gets all YouTube URL's corresponsing to queries(song names)
    
    Uses ThreadPoolEcecutor to invoke function "search_youtube" for getting URL's of 
    songs. The function "search_youtube" returns URL of a single song.
    
    Args: 
        queries (list): Name of songs stored in a list of strings.
            
    Returns: URL's of the songs or empty list if no urls are found.
    """
    urls = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(search_youtube, query): query for query in queries}
        for future in as_completed(futures):
            try:
                url = future.result()
                if url:
                    urls.append(url)
            except Exception as e:
                query = futures[future]  # Look up the query that caused the error
                print(f"Error fetching URL for '{query}': {e}")
    return urls

def download_all_ytube_urls(ytube_urls):
    """Gets all YouTube URL's corresponsing to queries(song names)
    
    Uses ThreadPoolEcecutor to invoke function "search_youtube" for getting URL's of 
    songs. The function "search_youtube" returns URL of a single song.
    
    Args: 
        ytube_urls (list): Name of URL's those are to be downloaded.
            
    Returns: Absolute filenames of the downloaded files
    """
    downloaded_files = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(download_youtube_audio_as_mp3, 
                    ytube_url):ytube_url for ytube_url in ytube_urls}
        for future in as_completed(futures):
            try:
                downloaded_file = future.result()
                if downloaded_file:
                    downloaded_files.append(downloaded_file)
            except Exception as e:
                ytube_url = futures[future]  # Look up the url that caused the error
                print(f"Error fetching video for '{ytube_url}': {e}")
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
    }
    
    # Download the video as audio using yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        # Extract the actual saved file name
        downloads = info_dict.get("requested_downloads", [])
        file_name = downloads[0].get("filepath") if downloads else None
     
    return file_name

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
    """Shortens a file name.
    
    The downloaded filenames are long. This function gets the absolute filename (pathname) 
    from "shorten_all_downloaded_file_names". The file is then renamed to a shorter name.
    The filename string is converted to a shorter string by calling the function 
    "return_short_string"   
         
    Args: 
        abs_path_out_file (string): Absolute path name of the file whose name is
        shortended.
                    
    Returns: Converted filename (Should be shorter than the original filename)
    """
    try:    
        folder, downloaded_file_name_with_ext = os.path.split(abs_path_out_file)
        only_filename, file_extension = os.path.splitext(downloaded_file_name_with_ext)
        short_filename = return_short_string(MY_NUM_FNAME_COMPONENTS, only_filename)
        new_file_name_with_ext =  short_filename + ".mp3"
        new_abs_path_of_mp3_file = os.path.join(folder, new_file_name_with_ext)
        os.rename(abs_path_out_file, new_abs_path_of_mp3_file)
        return new_file_name_with_ext
    except:
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
