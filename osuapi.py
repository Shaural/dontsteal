"""Get useful stuff from the osu!api"""
import base64
import lzma
import time
import requests
import mods
import json

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        OSU_API_KEY = config['osu_api_key']
except OSError as err:
    print("OS Error {0}".format(err))

def get_users_from_beatmap(beatmap_id):
    """Get users from top 100 scores."""
    parameters = {"k": OSU_API_KEY, "b": beatmap_id, "m": 0}
    api_request = requests.get("http://osu.ppy.sh/api/get_scores", params=parameters)
    json_data = api_request.json()
    users = []
    for item in json_data:
        enabled_mods = mods.get_mods(int(item["enabled_mods"]))
        users.append([item["username"], enabled_mods])
    return users


def get_replays(beatmap_id):
    """Get the replay data of a user's score on a beatmap."""
    replay_data = []
    for i, user in enumerate(get_users_from_beatmap(beatmap_id)):
        parameters = {"k": OSU_API_KEY, "b": beatmap_id, "m": 0, "u": user[0]}

        def download_replay():
            """Downloads and decodes a replay into a usable list"""
            req = requests.get("https://osu.ppy.sh/api/get_replay", params=parameters).json()
            try:
                print("\r({}/50) Downloading {}'s replay...               " .format(i+1, user[0]),
                      end="")
                replay_data.append([lzma.decompress(base64.b64decode(req["content"])).decode("utf-8"),
                                    user[1], user[0]])
                time.sleep(7)
            except KeyError as e:
                if req["error"] == "Requesting too fast! Slow your operation, cap'n!":
                    print("Too fast! Trying again in 15 seconds...")
                    time.sleep(15)
                    download_replay()
                else:
                    print(req)
                    raise e

        download_replay()
    print("")
    return replay_data


def get_beatmap(map_hash):
    """Retrieve general beatmap information and return beatmap ID"""
    parameters = {"k": OSU_API_KEY, "h": map_hash}
    requ = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters).json()
    return requ[0]["beatmap_id"]


def get_beatmap_info(beatmap_hash):
    """Retrieve general beatmap information."""
    beatmap_info = []
    parameters = {"k": OSU_API_KEY, "h": beatmap_hash}
    b_req = requests.get("https://osu.ppy.sh/api/get_beatmaps", params=parameters).json()
    beatmap_info.append("BEATMAP INFO: " + b_req[0]["artist"] + " - " + b_req[0]["title"]
                        + "[" + b_req[0]["version"] + "]")
    return beatmap_info
