import sys
import json
import operator
import requests
from .constants import constants
from .utilities import get_syllables, get_word_topics
from bs4 import BeautifulSoup
from .node import NodeInterface, ArtistNode, LyricNode
from .objects import AlbumObject, SongObject, SongAnalysisObject
from .artist_setup import artists_data

# Param: song_lyrics { String } - string with all the song lyrics
# Result: { Dictionary } - sorted dictionary containing a song with count per unique word
def lyric_analysis(song_lyrics):
    song_lyrics = song_lyrics.lower().replace(',','').replace('[','').replace(']','')
    lyric_list = song_lyrics.split()
    [lyric.lower() for lyric in lyric_list]
    my_dict = {}

    for item in lyric_list:
        if item in my_dict and (item not in constants["ignore"]): my_dict[item] += 1
        else: my_dict[item] = 1
    
    sorted_dict = sorted(my_dict.items(), key=operator.itemgetter(1), reverse=True)
    # top_results = sorted_dict[:15]  -- If you want top 15 results per song
    # --- For Individual Song Results ---
    # for item in top_results:
    #     try:
    #         print item[0], ',', item[1]
    #     except UnicodeEncodeError:
    #         print "Error on character"
    return sorted_dict

# Param: song { SongObject } - 
# Result: { SongAnalysisObject } - 
def song_analysis(song):
    analysis = SongAnalysisObject(song)
    song_lines = song.lyrics.split('\n')
    [[l.lower() for l in line] for line in song_lines]

    # Word Count
    analysis.word_count = len(song.lyrics.split())

    # Count Number of Times Each Word is Used in the Song
    word_counter = {}
    for line in song_lines:
        for lyric in line:
            if lyric in word_counter and (lyric not in constants["ignore"]): word_counter[lyric] += 1
            else: word_counter[lyric] = 1
    analysis.word_freq = word_counter

    # Count the number of Times Topics were referenced in a song
    topic_count = {}
    for word, count in word_counter.items():
        word_topics = get_word_topics(word)
        for t in word_topics:
            if t in topic_count: topic_count[t] += count
            else: topic_count[t] = count
    analysis.topic_refs = topic_count

    # Count the syllables per word in the song
    total_syllables = 0
    for word, count in word_counter.items():
        num_syllables = get_syllables(word)
        total_syllables += (num_syllables*count)
    analysis.syllables_per_word = total_syllables/float(analysis.word_count)
    
    return analysis

    


# Param: url { String } - url of a song to scrape the lyrics from
# Return: { SongObject } - Song object contents of id, url, title, and lyrics
def scrape_song(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.text, 'html.parser') 
    [element.extract() for element in inner_html('script')]

    # Get Lyrics from the song
    lyrics = inner_html.find('div', class_='lyrics').get_text()

    # Get the song ID and Title
    metadata = inner_html.find("meta", itemprop="page_data")
    data = json.loads(metadata["content"])
    
    song_id = data["song"]["id"]
    song_title = data["song"]["title"]
    song_release_date = data["song"]["release_date"]
    returnSong = SongObject(song_id,url,song_title,lyrics,song_release_date)


    return returnSong

# Param: url { String } - album url to be scraped for song urls and then processed
# Param: lyric_map { GraphObj } - graph containing current lyric and artist nodes
# Return: { AlbumObject } - Album Object containing all the album's data and lyric results, Updated Graph Object
def scrape_album(url,lyric_map = None):
    returnAlbum = AlbumObject()
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.content, 'html.parser')
    [el.extract() for el in inner_html('script')]

    try:
        # Scrape Album Metadata
        metadata = inner_html.find("meta", itemprop="page_data")
        data = json.loads(metadata["content"])
        print(data.keys())
        print(data["album"].keys())

        returnAlbum.title = data["album"]["name"]
        returnAlbum.id = data["album"]["id"]

        # Get other albums as suggestions to search
        for album in data["other_albums_by_artist"]:
            alb_url = album["url"]
            alb_url = alb_url.replace("https://genius.com/albums/","")
            returnAlbum.other_albums.append({album["name"]: alb_url})
        
        # Add album features to the album object returned
        for appearance in data["album_appearances"]:
            song_title = appearance["song"]["title"]
            # Remove all songs that are Genius Annotation Tracks and Booklet, Covers, etc. to scrape only the real songs
            if (not song_title.endswith(constants["song_title_ignore"])) and (not appearance["song"]["url"].endswith("-annotated")): 
                returnAlbum.song_ids[appearance["song"]["id"]] = song_title
                returnAlbum.song_urls.append(appearance["song"]["url"])
    
            for feat in appearance["song"]["featured_artists"]:
                if feat["is_verified"]:
                    if(feat["id"] not in returnAlbum.features["verified"]):
                        returnAlbum.features["verified"][feat["id"]] = feat["name"]
                else:
                    if(feat["id"] not in returnAlbum.features["unverified"]):
                        returnAlbum.features["unverified"][feat["id"]] = feat["name"]
        try:
            returnAlbum.release_year = data["album"]["release_date_components"]["year"]
            returnAlbum.release_date = data["album"]["release_date"]
        except TypeError:
            returnAlbum.release_year = -1
    
    except UnicodeEncodeError as e:
        print("Error",e)
    
    if lyric_map: AddAlbumToGraph(returnAlbum,lyric_map)
    return returnAlbum



def AddAlbumToGraph(returnAlbum,lyric_map):
    # Get all song urls to scrape from the respective album page
    # song_pages = inner_html.findAll('a', {"class": 'u-display_block'}, href=True)
    # song_urls = [s["href"] for s in song_pages]

    for song in returnAlbum.song_urls:

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
            returnAlbum.addLyricResult(res_key,res_val)

    return lyric_map


