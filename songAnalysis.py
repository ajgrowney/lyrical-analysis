import nltk
from nltk.probability import FreqDist

from Components.functions import scrape_song


lyrics = scrape_song('https://genius.com/Logic-fade-away-lyrics')


fdist = FreqDist(word.lower() for word in nltk.word_tokenize(lyrics.lyrics))
fdist.plot()
