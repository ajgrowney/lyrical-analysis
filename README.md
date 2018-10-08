# lyrical-analysis
Analyzing lyrics from the hip hop genre

## Artist Id Scraping
Description: Runs API calls for all of the range given, and creates objects for them in the provided filename
Command Line: python main.py artistId 1 2000 artistId.json

## Top Song Lyrics Search
Description: Searches Genius' API for the given song, uses the current artist ID's that you have scraped in your art_id.json file
Uses that list as criteria for searching for 'verified' artists
Command Line: python main.py search "Element" "Kung Fu Kenny"
