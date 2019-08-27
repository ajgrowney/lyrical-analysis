import requests
import json
from bs4 import BeautifulSoup
from test_object import TestSongObject, TestAlbumObject
from test_io import song_test, album_test

# Constants to test being used by main functions
constants = {
    "song_title_ignore": ("[Credits]", "[Tracklist + Album Art]","[Tracklist + Album Cover]", "[Booklet]"),
}

# Description: For testing purposes because snippet used in scrape_song function
# Param: url { String } - song url to be scraped for metadata
# Return: Test Song Object
def test_song_id(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.text, 'html.parser') 
    [element.extract() for element in inner_html('script')]
    # Get the song ID
    metadata = inner_html.find("meta", itemprop="page_data")
    data = json.loads(metadata["content"])
    song_id = data["song"]["id"]
    return song_id 
    

# Descrption: For testing purposes because snippet used in scrape_album func
# Param: url { String } - album url to be scraped for metadata
# Return: String, Int, Int, Dict, List - album name, the year it was released, album id, features, song urls
def test_album_data(url):
    html_page = requests.get(url)
    inner_html = BeautifulSoup(html_page.content, 'html.parser')
    [element.extract() for element in inner_html('script')]
    metadata = inner_html.find("meta", itemprop="page_data")
    try:
        data = json.loads(metadata["content"])
        appearances = data["album_appearances"]
        
        # Strip album features and song id with titles
        album_features = {"verified": {}, "unverified": {}}
        album_song_id = {}
        album_song_urls = []
        for ap in appearances:
            s = ap["song"]["title"]
            if (not s.endswith(constants["song_title_ignore"])) and (not ap["song"]["url"].endswith("-annotated")):
                album_song_id[ap["song"]["id"]] = s
                album_song_urls.append(ap["song"]["url"])
            for feature in ap["song"]["featured_artists"]:
                if feature["is_verified"]:
                    if (feature["id"] not in album_features["verified"]):
                        album_features["verified"][feature["id"]] = feature["name"]
                else:
                    if (feature["id"] not in album_features["unverified"]):
                        album_features["unverified"][feature["id"]] = feature["name"]

        # Get other albums by the artist in the database (TODO: Could add later)
        more_albums = data["other_albums_by_artist"]
      
        album_name = data["album"]['name']
        release_year = data["album"]["release_date_components"]["year"]
        album_id = data["album"]["id"]
        return album_name, release_year, album_id, album_features, album_song_id, album_song_urls
    except UnicodeEncodeError as e:
        print ("Error",e)

# Description: For testing purposes because snippet used in scrape_album
# Param url { String } - album url to be scraped for song urls
# Return: List<String> - song urls that scrape album will scrape 
# def test_album_songurls(url):
#     html_page = requests.get(url)
#     inner_html = BeautifulSoup(html_page.content, 'html.parser')
#     [el.extract() for el in inner_html('script')]
#     song_pages = inner_html.findAll('a', {"class": 'u-display_block'}, href=True)
#     song_urls = [s["href"] for s in song_pages]
#     return song_urls


def runTests(json_input, context):
    # Test Data
    successful_tests = 0
    failed_tests = 0
    # Song Testing Input
    songtest_input = song_test["input"]

    songid_expected = song_test["songid_output"]
    songtest_output = []
    for i in range(len(songtest_input)):
        ret_id = test_song_id("https://genius.com/"+songtest_input[i])
        retSongTest = TestSongObject(ret_id)
        songtest_output.append(retSongTest)
    print("\n---------Song ID Testing---------")
    for i in range(len(songtest_input)):
        returned_id = songtest_output[i].returned_id
        if(returned_id == songid_expected[i]):
            print("Test Success: " + songtest_input[i])
            successful_tests += 1
        else:
            print("Test Failed: " + songtest_input[i])
            print(returned_id,songid_expected[i])
            failed_tests += 1

    # Album Testing Input
    albumtest_input = album_test["input"]

    # Retrieving Testing Outputs 
    meta_expected = album_test["metadata_output"]
    test_output = []
    for i in range(len(albumtest_input)):
        ret_title, ret_year, ret_album_id, ret_features, ret_songids,ret_urls = test_album_data("https://genius.com/albums/"+albumtest_input[i])
        ret_title = ret_title.rstrip()
        retAlbumTest = TestAlbumObject(ret_title,ret_year,ret_album_id,ret_features,ret_songids,ret_urls) 
        test_output.append(retAlbumTest)

    print("\n---------Album Title/Year/ID Testing---------")
    for i in range(len(albumtest_input)):
        returned_title = test_output[i].returned_title
        returned_year = test_output[i].returned_year
        returned_album_id = test_output[i].returned_album_id

        if((meta_expected[i]["title"] == returned_title) and (meta_expected[i]["year"] == returned_year) and (returned_album_id == meta_expected[i]["id"])):
            print("Test Success: " + meta_expected[i]["title"])
            successful_tests += 1
        else:
            print("Test Failed: " + meta_expected[i]["title"]+ str(meta_expected[i]["id"])+ " " + str(meta_expected[i]["year"])+ " vs " + returned_title + " "+ str(returned_year)+" " + str(returned_album_id))
            failed_tests += 1
    
    # Testing Scrape Album's Song URL results
    songurl_expected = album_test["songurl_output"]

    print("\n---------Album Song URL Testing---------")
    for i in range(len(albumtest_input)):
        returned_urls = test_output[i].returned_songurls 
        full_expected = [("https://genius.com/"+s) for s in songurl_expected[i]]
        if(len(returned_urls) == len(full_expected)):
            error_count = 0

            if(set(returned_urls) == set(full_expected)):
                print("Test Success: " + albumtest_input[i])
                successful_tests += 1
            else:
                print("Failed on: " + str(error_count))
                failed_tests += 1
        else:
            print("Test Failed: " + str(len(full_expected)) + " vs " + str(len(returned_urls)))
            print(returned_urls)
            print("\n\n")
            print(full_expected)
            failed_tests += 1

    # Testing Album Features
    albumfeatures_expected = album_test["albumfeatures_output"]

    print("\n---------Album Features Testing---------")
    for i in range(len(albumtest_input)):
     returned_features = test_output[i].returned_features 
     if(returned_features == albumfeatures_expected[i]):
         successful_tests += 1
         print("Test Success: " + albumtest_input[i])
     else:
         failed_tests += 1
         print("Test Failed: " + str(albumfeatures_expected[i]) + " vs " + str(returned_features))
    
    # Testing Song IDs
    songids_expected = album_test["songids_output"]
    print("\n---------Song IDs Testing---------")
    for i in range(len(albumtest_input)):
        returned_songids = test_output[i].returned_songids 
        if(returned_songids == songids_expected[i]):
            successful_tests += 1
            print("Test Success: " + albumtest_input[i])
        else:
            failed_tests += 1
            print("Test Failed: " + str(songids_expected[i]) + " vs " + str(returned_songids))

    # Testing Results Total
    print("\n---------Testing Results---------")
    print("Expected Number of AWS Tests: "+ str(json_input["num_tests"]))
    print("Total Successful Tests: "+ str(successful_tests))
    print("Total Failed Tests: " + str(failed_tests))
    print("Testing Results: " + str(100 * float(successful_tests/(successful_tests+failed_tests))) + "%")

if __name__ == '__main__':
    runTests({"num_tests": 20},[])

