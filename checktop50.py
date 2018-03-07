"""Compares a replay against the top 50 of its beatmap"""
import sys
import os
import shutil
from glob import glob
import dontsteal
import download
from osrparse.replay import parse_replay_file

#Open Replay & Analyze
TARGET_REPLAY = parse_replay_file(sys.argv[1])
dontsteal.analyze(TARGET_REPLAY)
#Get Replay Events
TARGET_REPLAY_EVENTS = dontsteal.get_events_per_second(TARGET_REPLAY)
#Download Top 50 Replays
download.login(TARGET_REPLAY.beatmap_hash)
#Top 50 Replays
TOP_50_REPLAYS = []
DIRECTORY = os.getcwd()
PATTERN = "*.osr"

for dir, _, _ in os.walk(DIRECTORY):
    TOP_50_REPLAYS.extend(glob(os.path.join(dir, PATTERN)))

OUTPUT = ""
def pretty_print(text):
    """Print it better"""
    global OUTPUT
    OUTPUT += "%s\n" % text
    return

if not TOP_50_REPLAYS:
    print("Beatmap not ranked, can't download replays!")
    sys.exit(1)

print()
SUSPICIOUS = False
for rp in TOP_50_REPLAYS:

    replay_to_check = parse_replay_file(rp)
    rp_events = dontsteal.get_events_per_second(replay_to_check)
    comparison = dontsteal.compare_data(TARGET_REPLAY_EVENTS, rp_events)

    pretty_print("\nComparing to {}'s replay".format(replay_to_check.player_name))
    pretty_print("\nCases where the same keys were pressed: {}%%".format(comparison[1]) +
                 "\nCases where the pressed keys were different: {}%%".format(comparison[2]))

    if comparison[1] >= 95 and replay_to_check.player_name != TARGET_REPLAY.player_name:
        SUSPICIOUS = True
        print("""\nSuspicious same keys pressed percentage:
              {0:.2f}% with {top_player}'s replay""".format(comparison[1],
                                                            top_player=replay_to_check.player_name))
    pretty_print("Lowest values:")
    suspicious_low_values = True

    for values in sorted(comparison[0])[1:11]:
        if values >= 1:
            suspicious_low_values = False
        pretty_print(values)

    if suspicious_low_values and replay_to_check.player_name != TARGET_REPLAY.player_name:
        SUSPICIOUS = True
        print("""\nSuspicious lowest values with
              {top_player}'s replay""".format(top_player=replay_to_check.player_name))

    pretty_print("\nAverage of similarity:")
    average_value = sum(comparison[0]) / len(comparison[0])

    if average_value <= 15 and replay_to_check.player_name != TARGET_REPLAY.player_name:
        SUSPICIOUS = True
        print("\nNOTE: small value indicates a most likely copied replay")
        print("""Suspicious average of similarity:
              {0:.4f} with {top_player}'s replay""".format(average_value,
                                                           top_player=replay_to_check.player_name))
                                                           
    pretty_print(average_value)

if not SUSPICIOUS:
    print("\nNothing suspicious going on here!")

try:
    with open("analysis.txt", "w") as f:
        f.write(OUTPUT)
        f.close()
except OSError as error:
    print("OS Error: {0}".format(error))
    sys.exit(1)

shutil.rmtree(os.getcwd() + "/replays")
