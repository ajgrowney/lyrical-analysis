class AlbumObject:
    def __init__(self):
        self.id = -1
        self.title = ""
        self.release_year = -1
        self.lyric_results = {}
        # Holds dicts with key: title, val: url of album
        self.other_albums = []
        self.features = {
            "verified": {},
            "unverified": {}
        }
        self.song_ids = {}

class SongObject:
    def __init__(self):
        self.lyrics = ""
        self.id = -1
        self.title = ""
