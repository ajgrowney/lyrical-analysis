# References:
# https://medium.com/@ageitgey/quick-tip-speed-up-your-python-data-processing-scripts-with-process-pools-cf275350163a
# https://dev.to/willamesoares/how-to-integrate-spotify-and-genius-api-to-easily-crawl-song-lyrics-with-python-4o62

import json
import os
import operator
import sys
import time
import requests
from Components.constants import constants
from bs4 import BeautifulSoup
from Components.node import NodeInterface, ArtistNode, LyricNode
from Components.graph import GraphObj, GraphMenuObj
from Components.objects import AlbumObject, SongObject
from Components.artist_setup import artists_data
from Components.functions import scrape_song, scrape_album

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


# Description: Supports two main calls as of now:
# Song Search Analysis: takes in a song and artist, prints out top fifteen most used lyrics with option to exclude certain words
# Song Search Ex: python main.py 'search' "Element" "Kung Fu Kenny"
# Artist Id Retreival: takes in a range to make artist id api calls, creates a json file full of names that belong to that artist ID
# Artist Id Ex: python main.py 'artistId' 1 1000 art_id.json
def main():
    arg_len, user_input = len(sys.argv), sys.argv
    
    
    # In Progress: Main Functionality
    if arg_len == 2 and (user_input[1] == "mapSingle" or user_input[1] == "mapAll"):
        art_list = [artists_data["kendrick"]] if user_input != "mapAll" else [artists_data["pusha"],artists_data["chance"],artists_data["meek"],artists_data["kendrick"],artists_data["joey"]]
        lyrical_map = GraphObj(art_list)
        lyrical_map.mainMenuNav()

    elif arg_len == 2 and user_input[1] == "nlp":
        scrape_song("https://genius.com/Logic-run-it-lyrics")
    
    elif arg_len == 2 and user_input[1] == "scrapeAlbum":
        alb = scrape_album("https://genius.com/albums/Rush/Signals",lyric_map)
        print(alb.lyric_results)
    
    elif arg_len == 3 and user_input[1] == 'findArtistId':
            url = genius_api_call['base']
            params = {'q': user_input[2]}
            headers = {'Authorization': 'Bearer ' + genius_api_call['token']}
            res = requests.get(url+'/search',params=params, headers=headers).json()
            if res['meta']['status'] == 200:
                artist = res['response']['hits'][0]['result']['primary_artist']
                print(artist['name'],artist['id'])
        

    # Must be improved or deleted
    elif arg_len == 5 and user_input[1] == 'artistId':
        getArtistIdRange(user_input[2],user_input[3],user_input[4])
        
if __name__ == '__main__':
    main()
