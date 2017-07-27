import sys
import dontsteal
import download
import os
import shutil
from glob import glob
from osrparse.replay import parse_replay_file

# Open Replay & Analyze
targetReplay = dontsteal.open_replay()
dontsteal.analyze(targetReplay)

# Get Replay Events
targetReplayEvents = dontsteal.get_events_per_second(targetReplay)

# Download Top 50 Replays
download.login(targetReplay.beatmap_hash)

# Top 50 Replays
top50Replays = []
directory = os.getcwd()
pattern = "*.osr"

for dir, _, _ in os.walk(directory):
    top50Replays.extend(glob(os.path.join(dir, pattern)))

# print_chan? Really Shaural lol.
output = ""
def prettyPrint(text):
    global output
    output += "%s\n" % text
    return

if not top50Replays:
    print("Beatmap not ranked, can't download replays!")
    sys.exit(1)

print()
SUSPICIOUS = False
for rp in top50Replays:

    replayToCheck = parse_replay_file(rp)
    rpEvents = dontsteal.get_events_per_second(replayToCheck)

    comparison = dontsteal.compare_data(targetReplayEvents, rpEvents)

    prettyPrint("\nComparing to %s's replay" % replayToCheck.player_name)
    prettyPrint("\nCases where the same keys were pressed: %s%%" % comparison[1] +
               "\nCases where the pressed keys were different: %s%%" % comparison[2])

    if comparison[1] >= 95 and replayToCheck.player_name != targetReplay.player_name:
        SUSPICIOUS = True

        print("""\nSuspicious same keys pressed percentage:
              {0:.2f}% with {top_player}'s replay""".format(comparison[1],
                               
                                                            top_player=replayToCheck.player_name))
    prettyPrint("Lowest values:")

    suspicious_low_values = True

    for values in sorted(comparison[0])[1:11]:

        if values >= 1:
            suspicious_low_values = False

        prettyPrint(values)

    if suspicious_low_values and replayToCheck.player_name != targetReplay.player_name:

        SUSPICIOUS = True

        print("""\nSuspicious lowest values with
              {top_player}'s replay""".format(top_player=replayToCheck.player_name))

    prettyPrint("\nAverage of similarity:")

    average_value = sum(comparison[0]) / len(comparison[0])

    if average_value <= 15 and replayToCheck.player_name != targetReplay.player_name:
        SUSPICIOUS = True

        print("""\nSuspicious average of similarity:
              {0:.4f} with {top_player}'s replay""".format(average_value,
                                                           top_player=replayToCheck.player_name))

    prettyPrint(average_value)

if not SUSPICIOUS:
    print("\nNothing suspicious going on here!")

try:
    with open("analysis.txt", "w") as f:
        f.write(output)
        f.close()
except OSError as error:
    print("OS Error: {0}".format(error))
    sys.exit(1)

shutil.rmtree(os.getcwd() + "/replays")