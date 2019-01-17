# lyrical-analysis
I like music. But particularly, really, really good music. Not just the music that sounds appealing, but music that makes you think. Lyrics that push the audience. This application is just the beginning of what might push music and song writing to the next level. Simply, as of now, we are analyzing lyrics from the hip hop genre while utilizing test driven development.

## Constants
'apikey': {String} Create a genius developers account to obtain an API Key for searches <br />
'ignore': {List<String>} Ignore certain words when adding to the dictionary of lyrics <br />
'song_title_ignore': {Tuple<String>} Ignore song titles ending with these to reduce noise *get it*<br />
'verified_artists_path': {String} path to an existing json file that holds data with the example of art_id.json  <br />

## Testing
To run all the tests implements run: python Tests/test_basic.py <br />
Current Tests Implemented: <br />
Album Title and Year <br />
Album Song URL's <br />
Album Features <br />
Album Song ID's <br />

## Artist Map Initial
Description: This will be the main function that will be used to assemble the graph as a whole. As of now, I am adding features to continue building off the data structure in use
Command Line: python main.py artistMapInitial

## Artist Id Scraping
Description: Runs API calls for all of the range given, and creates objects for them in the provided filename <br />
Command Line: python main.py artistId 1 2000 artistId.json <br />
