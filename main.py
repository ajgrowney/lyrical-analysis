# References:
# https://medium.com/@ageitgey/quick-tip-speed-up-your-python-data-processing-scripts-with-process-pools-cf275350163a
# https://dev.to/willamesoares/how-to-integrate-spotify-and-genius-api-to-easily-crawl-song-lyrics-with-python-4o62

import json
import os
import operator
import sys
import time
import requests
import concurrent.futures
import matplotlib.pyplot as plt
from constants import constants
from multiprocessing.pool import ThreadPool as Pool
from bs4 import BeautifulSoup
from Components.node import NodeInterface, ArtistNode, LyricNode
from Components.graph import GraphObj
from Components.objects import AlbumObject, SongObject
from Data.artist_setup import artists_data

genius_api_call = {
    'token': constants["apikey"],
    'base': 'https://api.genius.com'
}

# Replace the filename with your own json object file if you have scraped lyrics
# Provided are artist IDs 1-8000 in the art_id.json file
if("verified_artists_path" in constants):
    try:
        verified_artists = json.load(open(constants["verified_artists_path"]))
    except IOError:
        verified_artists = False
        print("Invalid Verified Artist Path")

# Param: song_lyrics { String } - string with all the song lyrics
# Result: { Dictionary } - sorted dictionary containing a song with count per unique word
def lyric_analysis(song_lyrics):
    song_lyrics = song_lyrics.lower().replace(',','').replace('[','').replace(']','')
    lyric_list = song_lyrics.split()
    [lyric.lower() for lyric in lyric_list]
    my_dict = {}
    for item in lyric_list:
        item = item.encode('ascii','ignore').decode('utf-8')
        if item in my_dict and (item not in constants["ignore"]):
            my_dict[item] += 1
        else:
            my_dict[item] = 1
    sorted_dict = sorted(my_dict.items(), key=operator.itemgetter(1), reverse=True)
    # top_results = sorted_dict[:15]  -- If you want top 15 results per song
    # --- For Individual Song Results ---
    # for item in top_results:
    #     try:
    #         print item[0], ',', item[1]
    #     except UnicodeEncodeError:
    #         print "Error on character"
    return sorted_dict

# Param: url { String } - url of a song to scrape the lyrics from
# Return: string that holds all the lyrics text
def scrape_song(url):
    returnSong = SongObject()
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.text, 'html.parser') 
    [element.extract() for element in inner_html('script')]
    # Get Lyrics from the song
    lyrics = inner_html.find('div', class_='lyrics').get_text()
    # Get the song ID
    metadata = inner_html.find("meta", itemprop="page_data")
    data = json.loads(metadata["content"].encode('utf-8'))
    song_id = data["song"]["id"]
    song_title = data["song"]["title"].encode('ascii','ignore').decode('utf-8')
    returnSong.lyrics = lyrics
    returnSong.id = song_id
    returnSong.title = song_title
    return returnSong

# Param: url { String } - album url to be scraped for song urls and then processed
# Param: lyric_map { GraphObj } - graph containing current lyric and artist nodes
# Return: { AlbumObject, GraphObj } - Album Object containing all the album's data and lyric results, Updated Graph Object
def scrape_album(url,lyric_map):
    returnAlbum = AlbumObject()
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.content, 'html.parser')
    [el.extract() for el in inner_html('script')]

    try:
        # Scrape Album Metadata
        metadata = inner_html.find("meta", itemprop="page_data")
        data = json.loads(metadata["content"].encode('utf-8'))
        for appearance in data["album_appearances"]:
            song_title = appearance["song"]["title"].encode('ascii','ignore').decode('utf-8')
            returnAlbum.song_ids[appearance["song"]["id"]] = song_title
            for feat in appearance["song"]["featured_artists"]:
                if feat["is_verified"]:
                    if(feat["id"] not in returnAlbum.features["verified"]):
                        returnAlbum.features["verified"][feat["id"]] = feat["name"]
                else:
                    if(feat["id"] not in returnAlbum.features["unverified"]):
                        returnAlbum.features["unverified"][feat["id"]] = feat["name"]
        returnAlbum.release_year = data["album"]["release_date_components"]["year"]
        returnAlbum.title = data["album"]["name"]
        returnAlbum.id = data["album"]["id"]
    
    except UnicodeEncodeError as e:
        print "Error",e

    album_results = {}
    # Get all song urls to scrape from the respective album page
    song_pages = inner_html.findAll('a', {"class": 'u-display_block'}, href=True)
    song_urls = [s["href"] for s in song_pages]

    for song in song_urls:

        # Display the song url being scraped
        song_result = scrape_song(song)
        results = (lyric_analysis(song_result.lyrics))
        lyric_map.song_id_title[song_result.id] = song_result.title 
        print(song_result.title)

        # Dict Traversal: res_key, res_val = word, frequency
        for res_key,res_val in results:

            # --------Adding lyric to overall map-------
            # Lyric Exists in the node map
            if res_key in lyric_map.node_map:
                # Add Lyric to Timeline of the Lyric Node
                lyric_map.node_map[res_key].addLyricTimeline(returnAlbum.release_year,res_val)
                # Add Lyric to the Song References of the Lyric Node
                lyric_map.node_map[res_key].addLyricSongReferences(returnAlbum.release_year,song_result.id, song_result.title)
            else:
                newLyric = LyricNode(res_key)
                newLyric.timeline[returnAlbum.release_year] = res_val
                newLyric.song_references[returnAlbum.release_year] = [(song_result.id,song_result.title)]
                lyric_map.node_map[res_key] = newLyric
            
            # Adding lyric to individual album results
            if res_key in album_results:
                album_results[res_key] += res_val
            else:
                album_results[res_key] = res_val

    returnAlbum.lyric_results = album_results

    # Can be returned instead of album_results if you want a sorted array of lyrics from the album
    # sorted_album_results = []
    # for key, value in sorted(album_results.iteritems(), key=lambda (k,v): (v,k)):
    #     sorted_album_results.append((key,value))

    return returnAlbum, lyric_map


# Return: No return, only outputing song result
def print_song_result(song_info):
    if(verified_artists == False):
        print("No verified artists to search with")
        return
    if str(song_info['primary_artist']['id']) in verified_artists:
        try:
            print("** Song: "+ song_info['title'] + "**")
            print(song_info['primary_artist']['name'] + "\n")
        except UnicodeEncodeError:
            print("Unicode Error")

# Param: artist_in- Integer representing the artist id to make an api call for
# Return type: Object if valid response, Integer if error
# Example: getArtistId(5)
def getArtistId(artist_in):
    res_obj = {
        'alt_names': [],
        'name': ""
    }
    url = genius_api_call['base']
    headers = {'Authorization': 'Bearer ' + genius_api_call['token']}
    try:
        res = requests.get(url+'/artists/'+str(artist_in), headers=headers).json()
        if res['meta']['status'] == 200:
            if res['response']['artist']['is_verified']:
                for a in res['response']['artist']['alternate_names']:
                    res_obj['alt_names'].append(a)
                res_obj['name'] = res['response']['artist']['name'] 
                return res_obj
            
    except requests.exceptions.SSLError:
        return artist_in
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.RetryError as erre:
        print(erre)
    return res_obj

# Param: song- song to query for searching
# Param: artist- artist to query for searching
# Return: No return, prints out to console with song data
# Example: analyze_song("Element", "Kung Fu Kenny")
def analyze_song(song,artist):
    url = genius_api_call['base']
    params = {'q': song + ' ' + artist}
    headers = {'Authorization': 'Bearer ' + genius_api_call['token']}
    res = requests.get(url+'/search', params=params, headers=headers).json()

    if res['meta']['status'] == 200:
        for hit in res['response']['hits']:
            if hit['type'] == 'song':
                print_song_result(hit['result'])
                if(verified_artists == False):
                    print("Cannot analyze song with no verified artists")
                    return
                if(str(hit['result']['primary_artist']['id']) in verified_artists):
                    song_result = scrape_song(hit['result']['url'])
                    return lyric_analysis(song_result.lyrics)

# Param: range_start- Integer defining beginning artist id to retrieve
# Param: range_end- Integer defining last artist id to retrieve
# Param: filename- defining a .json file to create for object accessing
# About: Makes API calls for all numbers in the range and creating a file (json format) that holds artist data
# Return: Array<Integers> errors- containing the numbers that had api error responses
# Example: getArtistIdRange(1,1000, art_id.json)
def getArtistIdRange(range_start,range_end,filename):
    path = './id_results/'+filename
    err_path = './id_errors/err_'+filename

    artists = (json.load(open(path)) if(os.path.isfile(path) and os.access(path,os.R_OK)) else {} )
    errors = (json.load(open(err_path))['errors'] if(os.path.isfile(err_path) and os.access(err_path,os.R_OK)) else [])

    time_start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        r_st = int(range_start)
        r_end = int(range_end)
        for i,id_obj in zip(range(r_st,r_end), executor.map(getArtistId, range(r_st,r_end))):
            if i%((r_end-(r_st-1)) / 10) == 0:
                print("Next: ", i)
            if type(id_obj) == dict and id_obj['name'] != "":
                artists[i] = id_obj
            elif type(id_obj) == int:
                errors.append(i)
    
    time_end = time.time()
    print( "Artist Id Object file saved as: ",filename)
    print( "Execution time: ", time_end-time_start, " seconds")
    print( len(errors), "Errors remaining: ", errors)
    json.dump(artists, open(path,"w"))
    json.dump({"errors": errors}, open(err_path, "w"))
    return errors

# Param: lyric_map { GraphObj } - Graph object that holds node map to traverse
# Return: Nothing - returns when user requests to exit
def menuNavigation(lyric_map):
    menuChoice = 0
    menu = "1: View Artist Details\n2: View Word Details\n3: Exit\n "
    while(menuChoice != 3):
        print(menu)
        menuChoice = raw_input("Please Select: ")
        if menuChoice == '1':
            i=1
            selection = {}
            for name in lyric_map.artist_choices:
                selection[str(i)] = name
                print(i,name)
                i += 1
            choice = raw_input("Select an artist: ")
            artist = selection[choice]
            if artist in lyric_map.artist_choices:
                artist_id = lyric_map.artist_choices[artist]
                print lyric_map.node_map[artist_id].printDetails()
            else:
                print("Artist ID not found")
        elif menuChoice == '2':
            word = raw_input("Type a word to search: ")
            if word in lyric_map.node_map:
                print lyric_map.node_map[word].song_references
                print lyric_map.node_map[word].timeline
                #refs = lyric_map.node_map[word].song_references
                #chart = plt.bar(list(lyric_map.node_map[word].timeline.keys()), lyric_map.node_map[word].timeline.values(), color='g')
                #for rect, year in zip(chart, refs.keys()):
                #    height = rect.get_height()
                #    plt.text(rect.get_x() + rect.get_width()/2.0, height, ("\n".join((x[1] for x in (refs[year])))), ha='center', va='bottom')
                #plt.legend()
                #plt.show()
            else:
                print("Word not found. Try again")
        elif menuChoice == '3':
            return

# Description: Supports two main calls as of now:
# Song Search Analysis: takes in a song and artist, prints out top fifteen most used lyrics with option to exclude certain words
# Song Search Ex: python main.py 'search' "Element" "Kung Fu Kenny"
# Artist Id Retreival: takes in a range to make artist id api calls, creates a json file full of names that belong to that artist ID
# Artist Id Ex: python main.py 'artistId' 1 1000 art_id.json
def main():
    arg_len = len(sys.argv)
    user_input = sys.argv
    if arg_len == 3 and user_input[1] == 'findArtistId':
        url = genius_api_call['base']
        params = {'q': user_input[2]}
        headers = {'Authorization': 'Bearer ' + genius_api_call['token']}
        res = requests.get(url+'/search',params=params, headers=headers).json()
        if res['meta']['status'] == 200:
            artist = res['response']['hits'][0]['result']['primary_artist']
            print(artist['name'],artist['id'])
    # In Progress: Main Functionality
    if arg_len == 2 and user_input[1] == 'artistMapInitial':
        lyrical_map = GraphObj()

        art_list = [artists_data["pusha"],artists_data["chance"],artists_data["meek"],artists_data["kendrick"],artists_data["joey"]]

        for artist in art_list: 
            lyrical_map.artist_choices[artist["name"]] = artist["id"]
            new_art = ArtistNode(artist["name"],artist["id"])
            album_urls = artist["album_paths"]
            new_art.album_urls = album_urls

            running_total = {}        
            for album in new_art.album_urls:
                single_album,lyrical_map = scrape_album("https://genius.com/albums/"+new_art.album_search_str+'/'+album,lyrical_map)
                
                new_art.album_release_years[single_album.title] = single_album.release_year # Add the album year to the artist's node
                
                # Accumulate the albums lyrics to add to edges to artist's node
                for key,val in single_album.lyric_results.iteritems():
                    if key in running_total:
                        running_total[key] += val
                    else:
                        running_total[key] = val

            lyrical_map.node_map[artist["id"]] = new_art
        menuNavigation(lyrical_map) 
   
   # Testing Suite
    elif arg_len == 2 and user_input[1] == 'runTests':
        print("Testing has moved. To run tests: 'python Tests/test_basic.py'")
    # Album Data (Temporary) 
    elif arg_len == 2 and user_input[1] == 'songDataWork':
        scrape_song("https://genius.com/Kendrick-lamar-good-kid-lyrics")
   
    # Improve or Delete
    elif arg_len == 3 and user_input[1] == 'getArtistAtId':
        try:
            artist = verified_artists[user_input[2]]
            print verified_artists[user_input[2]]['name']
        except:
            print "Artist Not Found at id:",user_input[2]
    
    # Can be used for testing
    elif arg_len == 4 and user_input[1] == 'searchSingleSong':
        song, artist = user_input[2], user_input[3]
        lyric_dict = analyze_song(song,artist)
        print(lyric_dict)

    # Must be improved or deleted
    elif arg_len == 5 and user_input[1] == 'artistId':
        getArtistIdRange(user_input[2],user_input[3],user_input[4])
        
if __name__ == '__main__':
    main()
