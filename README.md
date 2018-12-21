# lyrical-analysis
Analyzing lyrics from the hip hop genre while utilizing test driven development

## Constants
'apikey': {String} Create a genius developers account to obtain an API Key for searches <br />
'ignore': {List<String>} Ignore certain words when adding to the dictionary of lyrics <br />
'verified_artists_path': {String} path to an existing json file that holds data with the example of art_id.json  <br />

## Testing
To run all the tests implements run: python main.py runTests <br />
Current Tests Implemented: <br />
Album Title and Year <br />
Album Song URL's <br />
Album Features <br />

## Artist Id Scraping
Description: Runs API calls for all of the range given, and creates objects for them in the provided filename <br />
Command Line: python main.py artistId 1 2000 artistId.json <br />

## Top Song Lyrics Search
Description: Searches Genius' API for the given song, uses the current artist ID's that you have scraped in your art_id.json file <br />
Uses that list as criteria for searching for 'verified' artists <br />
Command Line: python main.py search "Element" "Kung Fu Kenny" <br />
