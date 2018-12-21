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
from constants import constants
from multiprocessing.pool import ThreadPool as Pool
from bs4 import BeautifulSoup
from Components.node import NodeInterface, ArtistNode, LyricNode
from Components.graph import GraphObj
from Tests.metadata_test import metadata_test, songurl_test, albumfeatures_test

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
def scrape_lyrics(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.text, 'html.parser') 
    [element.extract() for element in inner_html('script')]

    lyrics = inner_html.find('div', class_='lyrics').get_text()
    return lyrics

# Descrption: For testing purposes because snippet used in scrape_album func
# Param: url { String } - album url to be scraped for metadata
# Return: String, Int, Int, Dict - album name, the year it was released, album id, and features
def scrape_album_data(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.content, 'html.parser')
    [element.extract() for element in inner_html('script')]
    metadata = inner_html.find("meta", itemprop="page_data")
    try:
        data = json.loads(metadata["content"].encode('utf-8'))
        appearances = data["album_appearances"]
        
        # Strip album features (Ideas: store just id's or data on which song?)
        album_features = {"verified": {}, "unverified": {}}
        for ap in appearances:
            for feature in ap["song"]["featured_artists"]:
                if feature["is_verified"]:
                    if (feature["id"] not in album_features["verified"]):
                        album_features["verified"][feature["id"]] = feature["name"]
                else:
                    if (feature["id"] not in album_features["unverified"]):
                        album_features["unverified"][feature["id"]] = feature["name"]

        # Get other albums by the artist in the database
        more_albums = data["other_albums_by_artist"]
        # for album in more_albums:
        #     if album["_type"] == "album":
        #         print album.keys(), album["name"], album["id"], album["artist"]["id"]
      
        album_name = data["album"]['name']
        release_year = data["album"]["release_date_components"]["year"]
        album_id = data["album"]["id"]
        return album_name, release_year, album_id, album_features
    except UnicodeEncodeError as e:
        print "Error",e

# Description: For testing purposes because snippet used in scrape_album
# Param url { String } - album url to be scraped for song urls
# Return: List<String> - song urls that scrape album will scrape 
def scrape_album_songurls(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.content, 'html.parser')
    [el.extract() for el in inner_html('script')]
    song_pages = inner_html.findAll('a', {"class": 'u-display_block'}, href=True)
    song_urls = [s["href"] for s in song_pages]
    return song_urls

# Param: url { String } - album url to be scraped for song urls and then processed
# Return: { Dict, Int, String} - Album lyrics results, Album Release Year, and Album Title
def scrape_album(url):
    album_results = {}
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.content, 'html.parser')
    [el.extract() for el in inner_html('script')]

    try:
        # Scrape Album Metadata
        metadata = inner_html.find("meta", itemprop="page_data")
        data = json.loads(metadata["content"].encode('utf-8'))
        
        release_year = data["album"]["release_date_components"]["year"]
        album_name = data["album"]["name"]
        album_id = data["album"]["id"]
    
    except UnicodeEncodeError as e:
        print "Error",e

    song_pages = inner_html.findAll('a', {"class": 'u-display_block'}, href=True)
    song_urls = [s["href"] for s in song_pages]
    for song in song_urls:
        print song
        song_lyrics = scrape_lyrics(song)
        results = (lyric_analysis(song_lyrics))
        for res_key,res_val in results:
            if res_key in album_results:
                album_results[res_key] += res_val
            else:
                album_results[res_key] = res_val

    sorted_album_results = []
    for key, value in sorted(album_results.iteritems(), key=lambda (k,v): (v,k)):
        sorted_album_results.append((key,value))
    #print(album_results)
    return album_results, release_year, album_name
    #print(sorted_album_results)


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
                    song_lyrics = scrape_lyrics(hit['result']['url'])
                    return lyric_analysis(song_lyrics)

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


# ------- In Progress -------------
def integrateArtist(artNode):
    url = genius_api_call['base']
    headers = {'Authorization': 'Bearer ' + genius_api_call['token']}
    print(artNode.id)
    try:
        res = requests.get(url+'/artists/'+str(artNode.id)+'/songs', headers=headers).json()
        if res['meta']['status'] == 200:
           for song in res['response']['songs']:
                if song['primary_artist']['id'] == artNode.id:
                    results = analyze_song(artNode.name,song['title'])
                    for res_key, res_val in results:
                        if res_key in artNode.adj_list:
                            artNode.adj_list[res_key] += res_val
                        else:
                            artNode.adj_list[res_key] = res_val
                    #print artNode.adj_list['in']
    except requests.exceptions.HTTPError as e:
        print(e)
    return artNode
    

# Description: Supports two main calls as of now: 
# Song Search Analysis: takes in a song and artist, prints out top fifteen most used lyrics with option to exclude certain words
# Song Search Ex: python main.py 'search' "Element" "Kung Fu Kenny"
# Artist Id Retreival: takes in a range to make artist id api calls, creates a json file full of names that belong to that artist ID
# Artist Id Ex: python main.py 'artistId' 1 1000 art_id.json
def main():
    arg_len = len(sys.argv)
    user_input = sys.argv

    # In Progress: Main Functionality
    if arg_len == 2 and user_input[1] == 'artistMapInitial':
        lyrical_map = GraphObj()
        kendrick = {"name": "Kendrick Lamar", "id": 1421, "albums": ["Good-kid-m-a-a-d-city","To-pimp-a-butterfly"]}
        jay = {"name": "Jay Z", "id": 2, "albums": ["4-44","Magna-carta-holy-grail"]}
        joey = {"name": "Joey Bada$$", "id": 3, "albums": ["All-amerikkkan-bada"]}
        logic = {"name": "Logic", "id": 7922, "albums": ["Under-pressure","The-incredible-true-story","Bobby-tarantino","Everybody","Bobby-tarantino-ii","Ysiv"]}
        art_list = [logic]

        for artist in art_list: 
            new_art = ArtistNode(artist["name"],artist["id"])
            album_urls = artist["albums"]
            new_art.album_urls = album_urls

            running_total = {}        
            for album in new_art.album_urls:
                single_album, album_year, album_name = scrape_album("https://genius.com/albums/"+new_art.album_search_str+'/'+album)
                
                new_art.album_release_years[album_name] = album_year # Add the album year to the artist's node
                
                # Accumulate the albums lyrics to add to edges to artist's node
                for key,val in single_album.iteritems():
                    if key in running_total:
                        running_total[key] += val
                    else:
                        running_total[key] = val
            real_total = {k:v for k,v in running_total.iteritems() if v != 1}
            print real_total
            lyrical_map.node_map[artist["id"]] = new_art

    # Very Useful for Testing
    elif arg_len == 2 and user_input[1] == 'runTests':

        # Test Data
        successful_tests = 0
        failed_tests = 0

        # Testing Album Title and Year Results
        meta_input = metadata_test["input"]
        meta_expected = metadata_test["output"]

        print("\n---------Album Title/Year Testing---------")
        for i in range(len(meta_input)):
            returned_title, returned_year, returned_album_id, returned_features = scrape_album_data("https://genius.com/albums/"+meta_input[i])
            returned_title = returned_title.rstrip()

            if(returned_title == meta_expected[i]["title"] and returned_year == meta_expected[i]["year"] and returned_album_id == meta_expected[i]["id"]):
                print("Test Success: " + meta_expected[i]["title"])
                successful_tests += 1
            else:
                print("Test Failed: " + meta_expected[i]["title"]+ str(meta_expected[i]["year"]) + " vs " + returned_title + " " + str(returned_year))
                failed_tests += 1
        
        # Testing Scrape Album's Song URL results
        songurl_input = songurl_test["input"]
        songurl_expected = songurl_test["output"]

        print("\n---------Album Song URL Testing---------")
        for i in range(len(songurl_input)):
            returned_urls = scrape_album_songurls("https://genius.com/albums/"+songurl_input[i])
            full_expected = [("https://genius.com/"+s) for s in songurl_expected[i]]
            if(len(returned_urls) == len(full_expected)):
                error_count = 0
                for j in range(len(returned_urls)):
                    if(returned_urls[j] != full_expected[j]):
                        error_count += 1
                        print(returned_urls[j] + " vs " + full_expected[j])
                if error_count == 0:
                    print("Test Success: " + songurl_input[i])
                    successful_tests += 1

                else:
                    print("Failed on: " + str(error_count))
                    failed_tests += 1
            else:
                print("Test Failed: " + str(len(full_expected)) + " vs " + str(len(returned_urls)))
                failed_tests += 1

        # Testing Album Features
        albumfeatures_input = albumfeatures_test["input"]
        albumfeatures_expected = albumfeatures_test["output"]

        print("\n---------Album Features Testing---------")
        for i in range(len(albumfeatures_input)):
            _, _, _, returned_features = scrape_album_data("https://genius.com/albums/"+albumfeatures_input[i])
            if(returned_features == albumfeatures_expected[i]):
                successful_tests += 1
                print("Test Success: " + albumfeatures_input[i])
            else:
                failed_tests += 1
                print("Test Failed: " + str(albumfeatures_expected[i]) + " vs " + str(returned_features))

        # Testing Results Total
        print("\n---------Testing Results---------")
        print("Total Successful Tests: "+ str(successful_tests))
        print("Total Failed Tests: " + str(failed_tests))
        print("Testing Results: " + str(100 * float(successful_tests/(successful_tests+failed_tests))) + "%")

    # Album Data Temporary 
    elif arg_len == 2 and user_input[1] == 'albumDataWork':
        scrape_album_data("https://genius.com/albums/Logic/The-incredible-true-story")
    # Improve or Delete
    elif arg_len == 3 and user_input[1] == 'getArtistAtId':
        try:
            artist = verified_artists[user_input[2]]
            print verified_artists[user_input[2]]['name']
        except:
            print "Artist Not Found at id:",user_input[2]
    
    # Must be improved or deleted
    elif arg_len == 3 and user_input[1] == 'addArtist':        
        
        artist_name = user_input[2]
        new_art = ArtistNode(artist_name,7922)
        integrateArtist(new_art)
        print("Results: ",new_art.adj_list)

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
