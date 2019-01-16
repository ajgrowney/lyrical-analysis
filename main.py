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
from Components.constants import constants
from multiprocessing.pool import ThreadPool as Pool
from bs4 import BeautifulSoup
from Components.node import NodeInterface, ArtistNode, LyricNode
from Components.graph import GraphObj
from Components.objects import AlbumObject, SongObject
from Components.artist_setup import artists_data

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
            lyrical_map.addNewArtist(artist)
        lyrical_map.mainMenuNav() 
   
   # Testing Suite
    elif arg_len == 2 and user_input[1] == 'runTests':
        print("Testing has moved. To run tests: 'python Tests/test_basic.py'")
    
    # Must be improved or deleted
    elif arg_len == 5 and user_input[1] == 'artistId':
        getArtistIdRange(user_input[2],user_input[3],user_input[4])
        
if __name__ == '__main__':
    main()
