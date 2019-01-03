
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
    def printDetails(self):
        print "Name:",self.name
        print "ID:",self.id
        print "Album urls searched:",self.album_urls
        print "Years with albums released:",self.album_release_years

    def addAlbumUrl(self,url):
        self.album_urls.append(url)

    def addConnection(self, key, val):
        self.adj_list[key] = val

class LyricNode(NodeInterface):
    def __init__(self, word):
        self.lyric = word
        self.id = word
        # Key: ID of a Node
        # Value: Refernece to that node
        self.adj_list = {}
        # Key: Year
        # Value: Number of times used that year
        self.timeline = {}
        # Key: Year
        # Value: Song ID
        self.song_references = {}
    def addConnection(self, key, val):
        self.adj_list[key] = val

