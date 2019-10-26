import types
import matplotlib.pyplot as plt
from .node import ArtistNode
from .functions import scrape_song, scrape_album

class GraphMenuObj:
    def __init__(self,choices = {}):
        self.choices = {i+1:x for i,x in enumerate(choices.keys())}
        self.actions = {i+1:y for i,y in enumerate(choices.values())}
        self.num_choices = len(choices)
    
    # Description: Iterate through menu options displaying all to user
    # Return: 
    def run(self):
        # Display Choices
        for index,choice in self.choices.items():
            print(str(index)+": "+choice)
        try:
            menuChoice = int(input("Please select: "))
        except ValueError as v:
            print("Invalid Input Type: use the corresponding number")
            return "Try Again"
        except KeyError as e:
            print("Invalid Menu Choice")
            return "Try Again"
        if type(self.actions[menuChoice]) == types.FunctionType:
            return self.actions[menuChoice](True)
        else: return self.actions[menuChoice]()

class GraphObj:
    def __init__(self,initial_artists = []):
        # Map for the Artist Search Menu {name: id}
        self.artist_choices = {}        
        # Map to access specific nodes {id: NodeObject}
        self.node_map = {}
        # Menu
        self.menu = GraphMenuObj({
            "View Artist Choice": self.ArtistMenu,
            "View Word Choice": lambda x: self.WordMenu(x),
            "Exit": self.ExitMenu
        })
        
        # Maps Song ID to Title {id: title}
        self.song_id_title = {}
        for artist in initial_artists:
            self.addToArtist(artist,True)

    def ExitMenu(self): return "exit"
    
    def ArtistMenu(self):
        selection = {}
        for i,name in zip(range(1,len(self.artist_choices)+1),self.artist_choices):
            selection[i] = name
            print(i,name)
        
        choice = int(input("Select an artist: "))
        artist = selection[choice]
        if artist in self.artist_choices:
            artist_id = self.artist_choices[artist]
            actions_returned = self.node_map[artist_id].printDetails()
            if actions_returned != None:
                print("Search more:", actions_returned)
                artist_data = {"id": artist_id, "album_paths": actions_returned}
                self.addToArtist(artist_data,False)
        else:
            print("Artist ID not found")

    def WordMenu(self,displayChart = False):
        word = input("Type a word to search: ")
        if word in self.node_map:
            print(self.node_map[word].topArtistConnections())
            print(self.node_map[word].song_references)
            print(self.node_map[word].timeline)
            if displayChart:
                refs = self.node_map[word].song_references
                chart = plt.bar(list(self.node_map[word].timeline.keys()), self.node_map[word].timeline.values(), color='g')
                for rect, year in zip(chart, refs.keys()):
                    height = rect.get_height()
                    plt.text(rect.get_x() + rect.get_width()/2.0, height, ("\n".join((x[1] for x in (refs[year])))), ha='center', va='bottom')
                plt.legend()
                plt.show()
        else:
            print("Word not found. Try again")

    def mainMenuNav(self):
        ret = ""
        while(ret != "exit"): ret = self.menu.run()
    

    def addToArtist(self, artist_input, new):
        artNode = {}
        suggested_albums = {}
        # New Artist Being Added
        if new or artist_input["id"] not in self.node_map:
            self.artist_choices[artist_input["name"]] = artist_input["id"]
            artNode = ArtistNode(artist_input["name"],artist_input["id"])
        else:
            artNode = self.node_map[artist_input["id"]]

        for album in artist_input["album_paths"]:
            # Move album from suggested to searched urls
            artNode.album_urls.append(album)
            if not new:
                del artNode.album_suggested[album]

            # Scrape album
            single_album = scrape_album("https://genius.com/albums/"+artNode.album_search_str+'/'+album,self)
                
            # Add other albums found to suggested searches for an artist
            for alb in (single_album.other_albums): 
                suggested_albums.update(alb)
            # Add the release year of the album to artist's release years
            artNode.album_release_years[single_album.title] = single_album.release_year
            # Accumulate the albums lyrics to add to edges to artist's node
            for key,val in single_album.lyric_results.items():
                cur_lyric = self.node_map[key]
                artNode.addLyricConnection(cur_lyric,val)
                cur_lyric.addArtistConnection(artNode,val)

            # Append suggested albums to artist node for further scraping
        for sug_title,sug_url in suggested_albums.items():
            # Remove the artists part of the string to normalize with other entries
            sug_url = sug_url.replace(artNode.album_search_str+"/",'')
            if sug_url not in artNode.album_urls:
                artNode.album_suggested[sug_url] = sug_title
        
        if new:
            self.node_map[artist_input["id"]] = artNode
