# dontsteal
_Stop stealing others' replays and git gud scrub!_

# Setup
* Run `python -m pip install -r requirements.txt`
* Create a config.json file
* Input your username, password, and [osu! API Key](https://osu.ppy.sh/p/api)
* Or just the API key

# NOTE
* Your username and password are required to connect and download replays faster instead of using osu!API
* If you still prefer using only the API write "-a" argument after the replay name (ex: `python checktop50.py replay.osr -a`) 
* Remember that this method it's quite slow (around 6 minutes) due to API rate limiting 

# Usage
* You can run `python dontsteal.py replay.osr replay2.osr` to compare two replays you have (change `replay` and `replay2` with the name of your replays)
* You can run `python checktop50.py replay.osr` to compare a replay with its beatmap top 50 in osu! (change `replay` with the name of your replay)

# Contributors
* [goeo_](https://github.com/goeo-) - Helped out with the initial logic.
* [Swan](https://github.com/Swan) - Added the possibility to use osu! accounts to download replays rather than the slow API.
 
 # LICENSE
 MIT License