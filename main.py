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
    top_results = sorted_dict[:15]

    # --- For Individual Song Results ---
    # for item in top_results:
    #     try:
    #         print item[0], ',', item[1]
    #     except UnicodeEncodeError:
    #         print "Error on character"
    return top_results

# Return: string that holds all the lyrics text
def scrape_lyrics(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.text, 'html.parser') 
    [element.extract() for element in inner_html('script')]

    lyrics = inner_html.find('div', class_='lyrics').get_text()
    return lyrics

def scrape_album(url):
    album_results = {}
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.content, 'html.parser')
    [el.extract() for el in inner_html('script')]
    song_pages = inner_html.findAll('a', {"class": 'u-display_block'}, href=True)
    song_urls = [s["href"] for s in song_pages]
    for song in song_urls:
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
    print(sorted_album_results)
    
# Return: Requests object, needs to be jsonified
def get_song_info(song, artist):
    url = genius_api_call['base']
    params = {'q': song + ' ' + artist}
    headers = {'Authorization': 'Bearer ' + genius_api_call['token']}
    return requests.get(url+'/search', params=params, headers=headers)

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
    res = get_song_info(song,artist).json()
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

    if arg_len == 2 and user_input[1] == 'scrapeAlbum':
        scrape_album("https://genius.com/albums/Kendrick-lamar/Good-kid-m-a-a-d-city")

    #----------In Progress---------
    if arg_len == 3 and user_input[1] == 'addArtist':
        artist_name = user_input[2]
        new_art = ArtistNode(artist_name,7922)
        integrateArtist(new_art)
        print("Results: ",new_art.adj_list)

    if arg_len == 4 and user_input[1] == 'search':
        song, artist = user_input[2], user_input[3]
        lyric_dict = analyze_song(song,artist)
        print(lyric_dict)

    elif arg_len == 5 and user_input[1] == 'artistId':
        getArtistIdRange(user_input[2],user_input[3],user_input[4])
        

                

if __name__ == '__main__':
    main()
