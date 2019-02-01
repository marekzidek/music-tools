import midi
import os
import logging
import argparse

def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-i', '--i', action='store', required=True,
                        help='input folder'),

    parser.add_argument('-o', '--o', action='store', required=True,
                        help='output folder'),

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def reorganize(index, steps, track):


    tick = track[index - steps].tick
    for i in range(index - steps + 1, index):

        if isinstance(track[i], midi.NoteEvent) and (isinstance(track[i], midi.NoteOffEvent) or track[i].velocity == 0):
            tmp = track[index - steps]
            tmp.tick = 0
            track[index - steps] = track[i]
            track[i] = tmp

    track[index - steps].tick = tick


def determine_free_channel(pattern):
    highest_channel = 0
    for t in pattern:
        for e in t:
            if hasattr(e, "channel") and e.channel > highest_channel:
                highest_channel = e.channel

    if highest_channel == 8:
        highest_channel += 1

    return highest_channel + 1


def rename_channel(channel, track_idx, track, pattern):
    print("called rename")
    # Find the channel
    referential_track = 0
    for t in pattern:
        for event in t:
            if hasattr(event, "channel"):
                if event.channel == channel:
                    referential_track = t
                    print("found ref track")
                    break
        if referential_track != 0:
            break


    # Detect which events to copy
    start = False
    evts_to_copy = []
    for event in referential_track:
        if start:
            evts_to_copy.append(event)

        if isinstance(event, midi.KeySignatureEvent) or isinstance(event,
                                                                   midi.ProgramChangeEvent):
            start = True

        if isinstance(event, midi.PortEvent) or isinstance(event,
                                                         midi.NoteEvent):
            break

    # Change all channel nrs in the track for an unused channel number except
    # for channel 9
    replacement_channel = determine_free_channel(pattern)
    print("replacement channel = {}".format(replacement_channel))
    for event in track:
        if hasattr(event, "channel"):
            event.channel = replacement_channel

    # Copy them

    new_track = midi.Track()
    new_track.extend(evts_to_copy)
    new_track.extend(track)

    print(track_idx)
    print(len(pattern))
    pattern[track_idx] = new_track

    return pattern


def check_max_nr_of_channels(pattern):

    to_remove = []
    for i, t in enumerate(pattern):
        for e in t:
            if hasattr(e, "channel"):
                if e.channel > 15:
                    to_remove.append(i)

    for index in sorted(to_remove, reverse=True):
        del pattern[index]

    return pattern


def correct(midifile):

    pattern = midi.read_midifile(midifile)
    used_channels = []

    for i in range(len(pattern)):
        track_channel_seen = False
        for event in pattern[i]:
            if hasattr(event,"channel") and not track_channel_seen:
                track_channel_seen = True
                if event.channel in used_channels:
                    rename_channel(event.channel, i, pattern[i], pattern)
                    break
                used_channels.append(event.channel)

    pattern = check_max_nr_of_channels(pattern)

    return pattern


if __name__ == "__main__":

    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


    if not os.path.exists(args.o):
        os.makedirs(args.o)

    for file in sorted(os.listdir(args.i)):

        print(file)

        pattern = correct(os.path.join(args.i, file))

        filename = os.path.join(args.o, file)

        if not filename.endswith('mid'):
            if not filename.endswith('midi'):
                filename += '.mid'

        midi.write_midifile(filename, pattern)

