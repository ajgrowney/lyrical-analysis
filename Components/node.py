
class NodeInterface:
    def __init__(self):
        print "Creating generic node"

class ArtistNode(NodeInterface):
    def __init__(self, name_in, id_in):
        self.name = name_in
        self.id = id_in # Genius Artist ID
        self.adj_list = {}
        print "Creating artist node:",self.name, self.id

    def addConnection(self, key, val):
        self.adj_list[key] = val

    def getAdjList(self):
        return self.adj_list

class LyricNode(NodeInterface):
    def __init__(self, word, id_in):
        self.lyric = word
        self.id = id_in # Lyric ID
        self.adj_list = {}
        print "Creating lyric node: ", self.lyric
    def addConnection(self, key, val):
        self.adj_list[key] = val

    def getAdjList(self):
        return self.adj_list
