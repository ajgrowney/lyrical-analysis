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
from math import ceil
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
        print "Invalid Verified Artist Path"

def lyric_analysis(song_lyrics):
    song_lyrics = song_lyrics.lower().replace(',','')
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
    for item in top_results:
        try:
            print item[0], ',', item[1]
        except UnicodeEncodeError:
            print "Error on character"
    return top_results

# Return: string that holds all the lyrics text
def scrape_lyrics(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.text, 'html.parser') 
    [element.extract() for element in inner_html('script')]

    lyrics = inner_html.find('div', class_='lyrics').get_text()
    return lyrics

# Return: Requests object, needs to be jsonified
def get_song_info(song, artist):
    url = genius_api_call['base']
    params = {'q': song + ' ' + artist}
    headers = {'Authorization': 'Bearer ' + genius_api_call['token']}
    return requests.get(url+'/search', params=params, headers=headers)

# Return: No return, only outputing song result
def print_song_result(song_info):
    if(verified_artists == False):
        print "No verified artists to search with"
        return
    if str(song_info['primary_artist']['id']) in verified_artists:
        try:
            print "** Song: "+ song_info['title'] + "**"
            print song_info['primary_artist']['name'] + "\n"
        except UnicodeEncodeError:
            print "Unicode Error"

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
        print errh
    except requests.exceptions.RetryError as erre:
        print erre
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
                    print "Cannot analyze song with no verified artists"
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

    if os.path.isfile(path) and os.access(path,os.R_OK):
        print "We in"
        artists = json.load(open(path))
    else:
        artists = {}

    if os.path.isfile(err_path) and os.access(err_path,os.R_OK):
        errors = json.load(open(err_path))['errors']
    else:
        errors = []
    
    time_start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
      for i,id_obj in zip(range(int(range_start),int(range_end)), executor.map(getArtistId, range(int(range_start),int(range_end)))):
        if i%((int(range_end)-(int(range_start)-1)) / 10) == 0:
            print "Next: ", i
        if type(id_obj) == dict and id_obj['name'] != "":
            artists[i] = id_obj
        elif type(id_obj) == int:
            errors.append(i)
    
    time_end = time.time()
    print "Artist Id Object file saved as: ",filename
    print "Execution time: ", time_end-time_start, " seconds"
    print len(errors), "Errors remaining: ", errors
    json.dump(artists, open(path,"w"))
    json.dump({"errors": errors}, open(err_path, "w"))
    return errors

# Description: Supports two main calls as of now: 
# Song Search Analysis: takes in a song and artist, prints out top fifteen most used lyrics with option to exclude certain words
# Song Search Ex: python main.py 'search' "Element" "Kung Fu Kenny"
# Artist Id Retreival: takes in a range to make artist id api calls, creates a json file full of names that belong to that artist ID
# Artist Id Ex: python main.py 'artistId' 1 1000 art_id.json
def main():
    arg_len = len(sys.argv)
    user_input = sys.argv
    if arg_len == 2 and user_input[1] == 'testObjectCreation':
        new_art = ArtistNode('Test',1)
        new_art.addConnection('Yo',3)
        print new_art.getAdjList()

    if arg_len == 4 and user_input[1] == 'search':
        song, artist = user_input[2], user_input[3]
        lyric_dict = analyze_song(song,artist)
        print lyric_dict

    elif arg_len == 5 and user_input[1] == 'artistId':
        getArtistIdRange(user_input[2],user_input[3],user_input[4])
        

                

if __name__ == '__main__':
    main()
