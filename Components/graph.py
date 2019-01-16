from node import ArtistNode
from functions import scrape_song, scrape_album

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
        menu = "1: View Artist Details\n2: View Word Details\n3: Exit\n "
        while(menuChoice != 3):
            print(menu)
            menuChoice = raw_input("Please Select: ")
            if menuChoice == '1':
                i=1
                selection = {}
                for name in self.artist_choices:
                    selection[str(i)] = name
                    print(i,name)
                    i += 1
                choice = raw_input("Select an artist: ")
                artist = selection[choice]
                if artist in self.artist_choices:
                    artist_id = self.artist_choices[artist]
                    print self.node_map[artist_id].printDetails()
                else:
                    print("Artist ID not found")
            elif menuChoice == '2':
                word = raw_input("Type a word to search: ")
                if word in self.node_map:
                    print self.node_map[word].song_references
                    print self.node_map[word].timeline
                    #refs = self.node_map[word].song_references
                    #chart = plt.bar(list(self.node_map[word].timeline.keys()), self.node_map[word].timeline.values(), color='g')
                    #for rect, year in zip(chart, refs.keys()):
                    #    height = rect.get_height()
                    #    plt.text(rect.get_x() + rect.get_width()/2.0, height, ("\n".join((x[1] for x in (refs[year])))), ha='center', va='bottom')
                    #plt.legend()
                    #plt.show()
                else:
                    print("Word not found. Try again")
            elif menuChoice == '3':
                return
    def addNewArtist(self, artist):
        if artist["id"] not in self.node_map:
            # Add Search Capabilities for artist to self object
            self.artist_choices[artist["name"]] = artist["id"]
    
            # Create new artist node
            new_art = ArtistNode(artist["name"],artist["id"])
            album_urls = artist["album_paths"]
            new_art.album_urls = album_urls
            suggested_albums = {}
            for album in new_art.album_urls:
                single_album,self = scrape_album("https://genius.com/albums/"+new_art.album_search_str+'/'+album,self)
                
                # Add other albums found to suggested searches for an artist
                for alb in (single_album.other_albums): 
                    suggested_albums.update(alb)
                # Add the release year of the album to artist's release years
                new_art.album_release_years[single_album.title] = single_album.release_year
                # Accumulate the albums lyrics to add to edges to artist's node
                for key,val in single_album.lyric_results.iteritems():
                    artist_connections = new_art.adj_list
                    cur_lyric = self.node_map[key]
                    if cur_lyric in artist_connections:
                        artist_connections[cur_lyric] += val
                    else:
                        artist_connections[cur_lyric] = val
            # Append suggested albums to artist node for further scraping
            for sug_title,sug_url in suggested_albums.iteritems():
                # Remove the artists part of the string to normalize with
                # other entries
                sug_url = sug_url.replace(new_art.album_search_str+"/",'')
                if sug_url not in new_art.album_urls:
                    new_art.album_suggested[sug_url] = sug_title
            self.node_map[artist["id"]] = new_art
        return self
    
