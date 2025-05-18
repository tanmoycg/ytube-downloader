from typing import Dict, List

def read_nameof_songs(textfile_song_names: str) -> List[Dict[str, str]]:
    """Reads input file with video/audio markers."""
    entries: List[Dict[str, str]] = []
    with open(textfile_song_names) as f:
        for line in f:
            if not (line := line.strip()):
                continue
            if line[0] in ('a', 'v'):
                entries.append({'type': line[0], 'query': line[1:].strip()})
    return entries