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

## Artist Map Initial
Description: This will be the main function that will be used to assemble the graph as a whole. As of now, I am buidling up the album scraping functionality so it can take in an artist's entire discography to create a well informed node
Command Line: python main.py artistMapInitial

## Artist Id Scraping
Description: Runs API calls for all of the range given, and creates objects for them in the provided filename <br />
Command Line: python main.py artistId 1 2000 artistId.json <br />

## Top Song Lyrics Search
Description: Searches Genius' API for the given song, uses the current artist ID's that you have scraped in your art_id.json file <br />
Uses that list as criteria for searching for 'verified' artists <br />
Command Line: python main.py search "Element" "Kung Fu Kenny" <br />
