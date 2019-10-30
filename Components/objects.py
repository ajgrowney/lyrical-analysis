class AlbumObject:
    def __init__(self):
        self.id = -1
        self.title = ""
        self.release_date = -1
        self.release_year = -1
        self.lyric_results = {}
        # Holds dicts with key: title, val: url of album
        self.other_albums = []
        self.features = {
            "verified": {},
            "unverified": {}
        }
        self.song_ids = {}
        self.song_urls = []

    def addLyricResult(self,lyric,freq):
        if lyric in self.lyric_results:
            self.lyric_results[lyric] += freq
        else:
            self.lyric_results[lyric] = freq

class SongObject:
    def __init__(self, _id = -1, _url = "", _title = "", _lyrics = "", _release_date = ""):
        self.id = _id
        self.url = _url
        self.title = _title
        self.lyrics = _lyrics
        self.release_date = _release_date

class SongAnalysisObject:
    def __init__(self,_songObject):
        self.songId = _songObject.id
        self.topic_refs = {}
        self.word_freq = {}
        self.syllables_per_word = -1.0
        self.release_date = _songObject.release_date
        self.word_count = -1

class ArtistObject:
    def __init__(self, _name = "", _id = -1, _city = "", _state = ""):
        self.name = _name
        self.id = _id
        self.city = _city
        self.state = _state

class LyricObject:
    def __init__(self, _word = "", _tags = []):
        self.word = _word
        self.tags = _tags

