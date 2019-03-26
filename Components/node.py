import operator
class NodeInterface:
    def __init__(self):
        print("Creating generic node")

class ArtistNode(NodeInterface):
    def __init__(self, name_in, id_in):
        search_str = name_in.replace(' ','-').replace('$','').lower().capitalize()
        self.name = name_in
        self.id = id_in # Genius Artist ID
        self.adj_list = {}
        self.album_search_str = search_str 
        self.album_urls = []
        self.album_suggested = {}
        self.album_release_years = {}
        print("Creating artist node:",self.name, self.id)
    
    def printDetails(self):
        menu = "\nMenu: "+self.name
        menu += "\n1: Artist Personal Info\n2: Lyrical Statistics\n3: Scrape More of Artist's Discography\n4: Exit"
        menuChoice = 0
        while menuChoice != 4:
            print(menu)
            menuChoice = raw_input("Make Selection: ")
            if menuChoice == '1':
                print("Name:",self.name)
                print("ID:",self.id)
            elif menuChoice == '2':
                # Artist's Lyric Statistics
                num_lyrics = 0
                total_word_length = 0
                unique_lyrics = 0 
                for key,val in self.adj_list.iteritems():
                    num_lyrics += val
                    total_word_length += len(key.lyric)*val
                    unique_lyrics += 1
                print("Number of lyrics searched:",num_lyrics)
                print("Number of unique lyrics:", unique_lyrics)
                print("Unique Lyric Ratio:", str(unique_lyrics/float(num_lyrics)))
                print("Average lyric length:", str(total_word_length/float(num_lyrics)))
                print("Years with albums released:",self.album_release_years)
                print("Album urls searched:",self.album_urls)
            elif menuChoice == '3':
                print("Albums suggested to search:",self.album_suggested.values())
                searchAll = raw_input("Search all suggested albums (y/N): ")
                if searchAll == 'y':
                    searchAlbumUrls = self.album_suggested.keys()
                    return searchAlbumUrls
            elif menuChoice == '4':
                return None



    def addAlbumUrl(self,url):
        self.album_urls.append(url)

    def addLyricConnection(self, lyric, val):
        if lyric in self.adj_list:
            self.adj_list[lyric] += val
        else:
            self.adj_list[lyric] = val

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

    def topArtistConnections(self):
        print(len(self.adj_list))
        sorted_artists = sorted(self.adj_list.items(), key = operator.itemgetter(1), reverse = True)
        return_artists = [(art.name,freq) for art,freq in sorted_artists[:3]]
        return return_artists
    def addArtistConnection(self, artist, val):
        if artist in self.adj_list:
            self.adj_list[artist] += val
        else:
            self.adj_list[artist] = val

    def addLyricTimeline(self, release_year, lyric_count):
        if release_year in self.timeline:
            self.timeline[release_year] += lyric_count
        else:
            self.timeline[release_year] = lyric_count

    def addLyricSongReferences(self, release_year, song_id, song_title):
        if release_year in self.song_references:
            self.song_references[release_year].append((song_id,song_title))
        else:
            self.song_references[release_year] = [(song_id,song_title)]
