import os
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
    lst_songs_for_download = read_nameof_songs(MY_FILE_OF_SONGS)
    print(lst_songs_for_download)
    cleanup_create(MY_DOWNLOAD_DIRECTORY)
    for song in lst_songs_for_download:
        youtube_url = search_youtube(song)
        if youtube_url:
            print(f"Found video: {youtube_url}")
            downloaded_file = download_youtube_audio_as_mp3(youtube_url)
            if downloaded_file:
                print(f"Download complete: {downloaded_file}")
            else:
                print(f"Download Unsuccessful: {youtube_url}")
        else:
           print(f"Could not find video for song : {song}")
    print("All Dowmloading finished") 
    
    print("Now Shortening the file names")
    # Get all files in the directory where songs were downloaded
    directory = os.path.join(Path.cwd(), MY_DOWNLOAD_DIRECTORY)
    all_files = [entry.name for entry in os.scandir(directory) if entry.is_file()]
    if all_files:
        for myfile in all_files:
            abspath = os.path.join(directory, myfile)
            shortname = rename_shorten_downloaded_file(abspath)
            if shortname:
                print(f"Renaming Successful : {shortname}")
            else:
                print(f"Could not Rename: {myfile}")
                
    else:
        print("No files were downloaded")
    
    print("Filenames Shortended ...Enjoy!!")
    return 0
 
def cleanup_create(directory):
    """ Removes the download directory, if it exists or creates it 
    if not exists
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
    """ read song names from text file and return a list of songs"""
    print(textfile_song_names)
    with open(textfile_song_names) as f:
        my_list = list(f)
        return [x.rstrip() for x in my_list]

def search_youtube(query, max_results=1):
    videos_search = VideosSearch(query, limit=max_results)
    results = videos_search.result()
    
    if results['result']:
        return results['result'][0]['link']  # Return the first result's URL
    else:
        return None

def download_youtube_audio_as_mp3(youtube_url, output_path=MY_DOWNLOAD_DIRECTORY, file_name=None):
    # Create downloads folder if it doesn't exist
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
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
        file_name = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
    
    return file_name

def rename_shorten_downloaded_file(abs_path_out_file):
    """ Save file with a shorter name"""
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
   """ This function restricts the number of words in a string to 
       num_of_words
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
