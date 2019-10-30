import nltk
import re
import sys
import pronouncing
from nltk.probability import FreqDist
from Utilities.geniusHelper import artistSongToUrl
from Components.functions import scrape_song

url = artistSongToUrl(sys.argv[1],sys.argv[2]) if len(sys.argv) > 2 else 'Logic-out-of-sight-lyrics'
song = scrape_song('https://genius.com/'+url)


lyrics = song.lyrics
lines = lyrics.split('\n')

# Remove unneccesary lines
regex = re.compile('\[*\]')
lines = list(filter(lambda i: i !='' and not regex.search(i),lines))

print(lines)