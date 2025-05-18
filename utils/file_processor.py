import os
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import MY_NUM_FNAME_COMPONENTS
from utils.string_utils import return_short_string

def shorten_all_downloaded_file_names(download_dir: str) -> List[str]:
    """Manages parallel filename shortening."""
    short_file_names: List[str] = []
    directory = os.path.join(os.getcwd(), download_dir)
    all_files = [entry.name for entry in os.scandir(directory) if entry.is_file()]
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(shorten_downloaded_file_name, 
                    os.path.join(directory, myfile)): myfile for myfile in all_files}
        for future in as_completed(futures):
            try:
                if short_file_name := future.result():
                    short_file_names.append(short_file_name)
            except Exception as e:
                myfile = futures[future]
                print(f"Error Renaming File for '{myfile}': {e}")
    return short_file_names

def shorten_downloaded_file_name(abs_path_out_file: str) -> Optional[str]:
    """Shortens individual filenames while preventing collisions."""
    try:    
        folder, filename = os.path.split(abs_path_out_file)
        name, ext = os.path.splitext(filename)
        short_name = return_short_string(MY_NUM_FNAME_COMPONENTS, name)
        new_path = os.path.join(folder, f"{short_name}{ext}")
        
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