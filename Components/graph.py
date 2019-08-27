import matplotlib.pyplot as plt
from .node import ArtistNode
from .functions import scrape_song, scrape_album

class GraphObj:
    def __init__(self):
        # Map for the Artist Search Menu {name: id}
        self.artist_choices = {}        
        # Map to access specific nodes {id: NodeObject}
        self.node_map = {}
        # Maps Song ID to Title {id: title}
        self.song_id_title = {}

    def mainMenuNav(self):
        menuChoice = 0
        menu = "\nMenu: Main Menu \n1: View Artist Details\n2: View Word Details\n3: Exit\n "

        while(menuChoice != 3):
            print(menu)
            menuChoice = input("Please Select: ")
            if menuChoice == '1':
                i=1
                selection = {}
                for name in self.artist_choices:
                    selection[str(i)] = name
                    print(i,name)
                    i += 1
                
                choice = input("Select an artist: ")
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
            elif menuChoice == '2':
                word = input("Type a word to search: ")
                if word in self.node_map:
                    print(self.node_map[word].topArtistConnections())
                    print(self.node_map[word].song_references)
                    print(self.node_map[word].timeline)
#                    refs = self.node_map[word].song_references
#                    chart = plt.bar(list(self.node_map[word].timeline.keys()), self.node_map[word].timeline.values(), color='g')
#                    for rect, year in zip(chart, refs.keys()):
#                        height = rect.get_height()
#                        plt.text(rect.get_x() + rect.get_width()/2.0, height, ("\n".join((x[1] for x in (refs[year])))), ha='center', va='bottom')
#                    plt.legend()
#                    plt.show()
                else:
                    print("Word not found. Try again")
            elif menuChoice == '3':
                return
    

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
