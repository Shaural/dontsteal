"""dontsteal - stop stealing replays and git gud scrub!"""
import math
import sys
from osrparse.replay import parse_replay_file
from osrparse.enums import GameMode, Mod

def analyze(replay):
    """Prints some common info about the replay"""
    if replay.game_mode is GameMode.Standard and replay.game_version >= 20140226:
        print("REPLAY INFO")
        print("Played by " + replay.player_name + " on " + replay.timestamp.__format__("%d/%m/%y %H:%M"))
        print("Mods used:")
        for mods_used in replay.mod_combination:
            print(str(mods_used).split("Mod.")[1])
        score = ["\nTotal Score: {}".format(replay.score),
                 "300s: {}".format(replay.number_300s),
                 "100s: {}".format(replay.number_100s),
                 "50s: {}".format(replay.number_50s),
                 "Gekis: {}".format(replay.gekis),
                 "Katus: {}".format(replay.katus),
                 "Misses: {}".format(replay.misses),
                 "Max Combo: {}".format(replay.max_combo)]
        for score_data in score:
            print(score_data)
        if replay.is_perfect_combo:
            print("Perfect Combo!\n")
        else:
            print("")
    else:
        raise ValueError("Can't analyze this replay, it might be too old or not for osu!standard.")
    return


def get_events_per_second(replay):
    """Gets coordinates and key pressed per second"""
    events = []
    time = 0

    for event in replay.play_data:
        time += event.time_since_previous_action
        if 1000*len(events) <= time:
            new_y = event.y if Mod.HardRock not in replay.mod_combination else 384-event.y
            events.append([event.x, new_y, event.keys_pressed])
    return events


def get_events_per_second_api(replay, mods):
    """Gets coordinates and key pressed per second for API"""
    events = []
    time = 0
    replay_events = replay.split(",")

    for event in replay_events:
        values = event.split("|")
        try:
            time += float(values[0])
        except ValueError:
            continue
        if 1000*len(events) <= time:
            new_y = float(values[2]) if "HR" not in mods else 384-float(values[2])
            events.append([float(values[1]), new_y, float(values[3])])
    return events


def compare_data(positions1, positions2):
    """Compares coordinates and key pressed between the two replays"""
    length = len(positions1) if len(positions1) <= len(positions2) else len(positions2)
    closeness = []
    same_keys_pressed = 0
    not_same_keys_pressed = 0

    for rep_value in range(0, length - 1):
        first_p = positions1[rep_value]
        second_p = positions2[rep_value]
        x_value = first_p[0] - second_p[0]
        y_value = first_p[1] - second_p[1]
        closeness.append(math.sqrt(x_value ** 2 + y_value ** 2))
        if first_p[2] == second_p[2]:
            same_keys_pressed += 1
        else:
            not_same_keys_pressed += 1

    same_key_percentage = (100 * same_keys_pressed) / (same_keys_pressed + not_same_keys_pressed)
    different_key_percentage = 100 - same_key_percentage
    return closeness, same_key_percentage, different_key_percentage


if __name__ == "__main__":
    first_replay = parse_replay_file(sys.argv[1])
    second_replay = parse_replay_file(sys.argv[2])

    if(first_replay.beatmap_hash != second_replay.beatmap_hash):
        sys.exit("""
        ! ERROR: beatmap is not the same !
        """)
    elif(first_replay.player_name == second_replay.player_name):
        sys.exit("""
        ! ERROR: replays from the same player !
        """)

    print("""
    --- 1st Replay Data ---
    """)
    analyze(first_replay)
    print("""
    --- 2nd Replay Data ---
    """)
    analyze(second_replay)

    print("""
    ---- Analysis Results ----
    """)
    first_replay_positions = get_events_per_second(first_replay)
    second_replay_positions = get_events_per_second(second_replay)
    comparison = compare_data(first_replay_positions, second_replay_positions)
    avg_similarity = sum(comparison[0]) / len(comparison[0])
    same_keys = comparison[1]
    different_keys = comparison[2]

    print("\nLowest values:")
    for lowest_values in sorted(comparison[0])[2:12]:
        print(lowest_values)

    print("\nAverage of similarity:")
    print("{0:.4f}\n".format(avg_similarity))

    if (avg_similarity) <= 15:
        print("""
        ! ALERT: possible copied replay !
        \n""")

    print("Cases where the same keys were pressed: {0:.2f}%\n".format(same_keys) +
        "Cases where the pressed keys were different: {0:.2f}%\n".format(different_keys) +
        "(Might not be accurate for some beatmaps)")
