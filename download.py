import http.cookiejar
import urllib.parse
import urllib.request
import sys
import json
import requests
import os

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

with open('config.json', 'r') as f:
    config = json.load(f)

# Gets JSON data from a given URL
def getJSON(url):
    try:
        data = requests.get(url=url).json()
        return data   
    except requests.exceptions.Timeout:
        data = requests.get(url=url).json()
    except requests.exceptions.TooManyRedirects:
        print("Invalid link given")
    except requests.exceptions.RequestException as e:
        print (e)


# Responsible for logging into the osu! website 
def login(beatmapMd5):
    print("Attempting to log into the osu! website...")

    payload = {
        'username': config['username'],
        'password': config['password'],
        'redirect': 'https://osu.ppy.sh/forum/ucp.php',
        'sid': '',
        'login': 'login'
    }

    payload = urllib.parse.urlencode(payload).encode("utf-8")
    response = opener.open("https://osu.ppy.sh/forum/ucp.php?mode=login", payload)

    data = bytes(str(response.read()), "utf-8").decode("unicode_escape")

    # Check if invalid credentials were given
    if "incorrect password" in data:
        print("You have specified an invalid password. Please check config.json")
        sys.exit()

    print("Successfully logged into the osu! website!")
    return getScores(beatmapMd5)


# Gets all scores for a given beatmap.
def getScores(beatmapMd5):
    # Get beatmap_id from md5 hash
    url = 'https://osu.ppy.sh/api/get_beatmaps?k={}&h={}&mode=0&limit=50'.format(config['osu_api_key'], beatmapMd5)
    beatmapData = getJSON(url)

    if len(beatmapData) < 1:
        print("The beatmap is either invalid or not ranked on osu!")
        sys.exit()
    
    beatmapDataString = """
    ------------------------------------------------
    | Comparing Replays For Map:
    | Artist: {}
    | Title: {}
    | Beatmap Id: {}
    ------------------------------------------------
    """.format(beatmapData[0]['artist'], beatmapData[0]['title'], beatmapData[0]['beatmap_id'])
    print(beatmapDataString)

    # Get list of score ids from beatmap
    scoreUrl = 'https://osu.ppy.sh/api/get_scores?k={}&b={}&mode=0&limit=50'.format(config['osu_api_key'], beatmapData[0]['beatmap_id'])
    scoreData = getJSON(scoreUrl)

    scoreIds = []
    for score in scoreData:
        scoreIds.append(score['score_id'])
        
    return downloadReplays(scoreIds)

# Takes a list of scoreIds and downloads the replay to a new directory.
def downloadReplays(scoreIds):
    # Create a new path for the replays to be housed.
    newPath = os.getcwd() + "/" + "replays"
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    for scoreId in scoreIds:
        try:
            directory = os.path.join(newPath)
            fullPath = directory + "/" + str(scoreId) + ".osr"
            print("\rDownloading Replay: {}..." .format(scoreId), end="")

            url = 'https://osu.ppy.sh/web/osu-getreplay.php?c={}&m=0'.format(scoreId)
            f = opener.open(url, {})
            data = f.read()
            with open(fullPath, 'wb') as code:
                code.write(data)
        except Exception as e:
            print(e)
            sys.exit()
