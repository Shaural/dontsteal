"""Compares a replay against the top 50 of its beatmap"""
import sys
import os
import shutil
import dontsteal
import download
import osuapi
from glob import iglob
from osrparse.replay import parse_replay_file

#delete log file on every run
if(os.path.exists("analysis_log.txt")):
    os.remove("analysis_log.txt")

#open replay & analyze
TARGET_REPLAY = parse_replay_file(sys.argv[1])
dontsteal.analyze(TARGET_REPLAY)
#get replay events
TARGET_REPLAY_EVENTS = dontsteal.get_events_per_second(TARGET_REPLAY)
#empty list to be filled with replays
TOP_50_REPLAYS = []
#empty string for logging
OUTPUT = ""


def log_print(text):
    """Print it cool for logging"""
    global OUTPUT
    OUTPUT += "%s\n" % text
    return


#comparing replays using osu!API data 
if(len(sys.argv) == 3 and sys.argv[2] == "-a"):
    #download top 50 replays using data from osu!API
    osuapi.get_beatmap_info(TARGET_REPLAY.beatmap_hash)
    TOP_50_REPLAYS = osuapi.get_replays(osuapi.get_beatmap(TARGET_REPLAY.beatmap_hash))

    if not TOP_50_REPLAYS:
        sys.exit("Beatmap not ranked, can't download replays!")

    print("""\n

    ---- Analysis Results ----
    """)
    SUSPICIOUS = False
    for rp_api in TOP_50_REPLAYS:
        rp_events = dontsteal.get_events_per_second_api(rp_api[0], rp_api[1])
        comparison = dontsteal.compare_data(TARGET_REPLAY_EVENTS, rp_events)

        log_print("Comparing to {}'s replay".format(rp_api[2]))

        # closeness
        log_print("Lowest values:")
        suspicious_low_values = True
        for values in sorted(comparison[0])[1:11]:
            if values >= 1:
                suspicious_low_values = False
            log_print(values)

        if suspicious_low_values and rp_api[2] != TARGET_REPLAY.player_name:
            SUSPICIOUS = True
            print("\nSuspicious lowest values with {top_player}'s replay".format(top_player=rp_api[2]))

        log_print("\nAverage of similarity:")
        average_value = sum(comparison[0]) / len(comparison[0])
        log_print(average_value)

        if average_value <= 15 and rp_api[2] != TARGET_REPLAY.player_name:
            SUSPICIOUS = True
            print("""
            ! ALERT: possible copied replay detected !
            """)
            print("Suspicious average of similarity: {0:.4f} with {top_player}'s replay".format(average_value, top_player=rp_api[2]))

        # key pressed
        log_print("\nCases where the same keys were pressed: {}%%".format(comparison[1]) + 
                    "\nCases where the pressed keys were different: {}%%".format(comparison[2]))

        if comparison[1] >= 95 and rp_api[2] != TARGET_REPLAY.player_name:
            SUSPICIOUS = True
            print("Suspicious same keys pressed percentage: {0:.2f}% with {top_player}'s replay\n".format(comparison[1], top_player=rp_api[2]))

    if not SUSPICIOUS:
        print("Nothing suspicious going on here!")

#comparing data from downloaded osr files
elif(len(sys.argv) == 2):
    #download top 50 replays using account login method
    download.login(TARGET_REPLAY.beatmap_hash)
    DIRECTORY = os.getcwd() + "/replays"
    PATTERN = "*.osr"

    for dir, _, _ in os.walk(DIRECTORY):
        TOP_50_REPLAYS.extend(iglob(os.path.join(dir, PATTERN)))
    
    if not TOP_50_REPLAYS:
        sys.exit("Beatmap not ranked, can't download replays!")

    print("""\n

    ---- Analysis Results ----
    """)

    SUSPICIOUS = False
    for rp in TOP_50_REPLAYS:
        replay_to_check = parse_replay_file(rp)
        rp_events = dontsteal.get_events_per_second(replay_to_check)
        comparison = dontsteal.compare_data(TARGET_REPLAY_EVENTS, rp_events)

        log_print("\nComparing to {}'s replay".format(replay_to_check.player_name))

        # closeness
        log_print("Lowest values:")
        suspicious_low_values = True
        for values in sorted(comparison[0])[1:11]:
            if values >= 1:
                suspicious_low_values = False
            log_print(values)

        if suspicious_low_values and replay_to_check.player_name != TARGET_REPLAY.player_name:
            SUSPICIOUS = True
            print("\nSuspicious lowest values with {top_player}'s replay".format(top_player=replay_to_check.player_name))

        log_print("\nAverage of similarity:")
        average_value = sum(comparison[0]) / len(comparison[0])
        log_print(average_value)

        if average_value <= 15 and replay_to_check.player_name != TARGET_REPLAY.player_name:
            SUSPICIOUS = True
            print("""
            ! ALERT: possible copied replay detected !
            """)
            print("Suspicious average of similarity: {0:.4f} with {top_player}'s replay".format(average_value, top_player=replay_to_check.player_name))

        # key pressed
        log_print("\nCases where the same keys were pressed: {}%%".format(comparison[1]) + 
                    "\nCases where the pressed keys were different: {}%%".format(comparison[2]))

        if comparison[1] >= 95 and replay_to_check.player_name != TARGET_REPLAY.player_name:
            SUSPICIOUS = True
            print("Suspicious same keys pressed percentage: {0:.2f}% with {top_player}'s replay\n".format(comparison[1], top_player=replay_to_check.player_name))
                                                            
    if not SUSPICIOUS:
        print("Nothing suspicious going on here!")

    shutil.rmtree(os.getcwd() + "/replays")


try:
    with open("analysis_log.txt", "w") as f:
        f.write(OUTPUT)
        f.close()
except OSError as error:
    print("OS Error: {0}".format(error))
    sys.exit(1)
