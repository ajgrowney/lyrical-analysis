import json
import concurrent.futures
from multiprocessing.pool import ThreadPool as Pool

def artistSongToUrl(artist, song):
    artistUrl = artist.lower().replace(' ','-').replace('$','')
    songUrl = song.lower().replace(' ','-')
    fullUrl = (artistUrl+'-'+songUrl+'-lyrics').capitalize()
    return(fullUrl)


# Param: range_start- Integer defining beginning artist id to retrieve
# Param: range_end- Integer defining last artist id to retrieve
# Param: filename- defining a .json file to create for object accessing
# About: Makes API calls for all numbers in the range and creating a file (json format) that holds artist data
# Return: Array<Integers> errors- containing the numbers that had api error responses
# Example: getArtistIdRange(1,1000, art_id.json)
def getArtistIdRange(range_start,range_end,filename):
    path = './id_results/'+filename
    err_path = './id_errors/err_'+filename

    artists = (json.load(open(path)) if(os.path.isfile(path) and os.access(path,os.R_OK)) else {} )
    errors = (json.load(open(err_path))['errors'] if(os.path.isfile(err_path) and os.access(err_path,os.R_OK)) else [])

    time_start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        r_st = int(range_start)
        r_end = int(range_end)
        for i,id_obj in zip(range(r_st,r_end), executor.map(getArtistId, range(r_st,r_end))):
            if i%((r_end-(r_st-1)) / 10) == 0:
                print("Next: ", i)
            if type(id_obj) == dict and id_obj['name'] != "":
                artists[i] = id_obj
            elif type(id_obj) == int:
                errors.append(i)
    
    time_end = time.time()
    print( "Artist Id Object file saved as: ",filename)
    print( "Execution time: ", time_end-time_start, " seconds")
    print( len(errors), "Errors remaining: ", errors)
    json.dump(artists, open(path,"w"))
    json.dump({"errors": errors}, open(err_path, "w"))
    return errors

