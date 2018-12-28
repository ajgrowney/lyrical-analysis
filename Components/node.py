
class NodeInterface:
    def __init__(self):
        print "Creating generic node"

class ArtistNode(NodeInterface):
    def __init__(self, name_in, id_in):
        self.name = name_in
        self.id = id_in # Genius Artist ID
        self.adj_list = {}
        self.album_search_str = name_in.replace(' ','-').replace('$','')
        self.album_urls = []
        self.album_release_years = {}
        print "Creating artist node:",self.name, self.id
    
    def addAlbumUrl(self,url):
        self.album_urls.append(url)

    def addConnection(self, key, val):
        self.adj_list[key] = val

class LyricNode(NodeInterface):
    def __init__(self, word):
        self.lyric = word
        self.id = word
        self.adj_list = {}
        self.timeline = {}
        self.song_references = {}
    def addConnection(self, key, val):
        self.adj_list[key] = val

