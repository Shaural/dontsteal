"""Download replays from osu! website"""
import http.cookiejar
import urllib.parse
import urllib.request
import sys
import json
import os
import requests

JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(JAR))

with open('config.json', 'r') as f:
    CONFIG = json.load(f)
    f.close()

def get_json(url):
    """Gets JSON data from a given URL"""
    try:
        data = requests.get(url=url).json()
        return data
    except requests.exceptions.Timeout:
        data = requests.get(url=url).json()
    except requests.exceptions.TooManyRedirects:
        print("Invalid link given")
    except requests.exceptions.RequestException as err:
        print(err)


def login(beatmap_md5):
    """Responsible for logging into the osu! website """
    print("Attempting to log into the osu! website...")
    payload = {
        'username': CONFIG['username'],
        'password': CONFIG['password'],
        'redirect': 'https://osu.ppy.sh/forum/ucp.php',
        'sid': '',
        'login': 'login'
    }
    payload = urllib.parse.urlencode(payload).encode("utf-8")
    response = OPENER.open("https://osu.ppy.sh/forum/ucp.php?mode=login", payload)
    data = bytes(str(response.read()), "utf-8").decode("unicode_escape")

    #check if invalid credentials were given
    if "incorrect password" in data:
        sys.exit("You have specified an invalid password. Please check config.json")

    print("Successfully logged into the osu! website!")
    return get_scores(beatmap_md5)


def get_scores(beatmap_md5):
    """Gets all scores for a given beatmap."""
    #get beatmap_id from md5 hash
    url = 'https://osu.ppy.sh/api/get_beatmaps?k={}&h={}&mode=0&limit=50'.format(CONFIG['osu_api_key'], beatmap_md5)
    beatmap_data = get_json(url)

    if len(beatmap_data) < 1:
        sys.exit("The beatmap is either invalid or not ranked on osu!")

    beatmap_data_string = """
    ------------------------------------------------
    | Comparing Replays For Map:
    | Artist: {}
    | Title: {}
    | Beatmap Id: {}
    ------------------------------------------------
    """.format(beatmap_data[0]['artist'], beatmap_data[0]['title'], beatmap_data[0]['beatmap_id'])
    print(beatmap_data_string)

    #get list of score ids from beatmap
    score_url = 'https://osu.ppy.sh/api/get_scores?k={}&b={}&mode=0&limit=50'.format(CONFIG['osu_api_key'], beatmap_data[0]['beatmap_id'])
    score_data = get_json(score_url)

    score_ids = []
    for score in score_data:
        score_ids.append(score['score_id'])

    return download_replays(score_ids)


def download_replays(score_ids):
    """Takes a list of scoreIds and downloads the replay to a new directory."""
    #create a new path for the replays to be housed.
    new_path = os.getcwd() + "/" + "replays"
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    for score_id in score_ids:
        try:
            directory = os.path.join(new_path)
            full_path = directory + "/" + str(score_id) + ".osr"
            print("\rDownloading replay: {}..." .format(score_id), end="")

            url = 'https://osu.ppy.sh/web/osu-getreplay.php?c={}&m=0'.format(score_id)
            f_2 = OPENER.open(url, {})
            data = f_2.read()
            with open(full_path, 'wb') as code:
                code.write(data)
                code.close()
        except IOError as err:
            print(err)
            sys.exit()
