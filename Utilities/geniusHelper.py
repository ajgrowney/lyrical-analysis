
def artistSongToUrl(artist, song):
    artistUrl = artist.lower().replace(' ','-').replace('$','')
    songUrl = song.lower().replace(' ','-')
    fullUrl = (artistUrl+'-'+songUrl+'-lyrics').capitalize()
    return(fullUrl)
