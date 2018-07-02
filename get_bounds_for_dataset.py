from __future__ import print_function
import midi
import argparse
import os

# This script is used for analysis of a dataset and prints out the min and max span note-span of it.

def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--dataset', action='store', required=True,
                        help='Dataset to analyze')


    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def proccess_pattern(pattern, highest, lowest):

    remainingTime = [track[0].tick for track in pattern]
    positionInTrack = [0 for track in pattern]

    while not (all(t is None for t in remainingTime)):
        for i in range(len(remainingTime)):
            while remainingTime[i] == 0:

                track = pattern[i]
                pos = positionInTrack[i]

                event = track[pos]
                if isinstance(event, midi.TimeSignatureEvent):
                    if event.numerator not in (2, 4) and not ignore_rhythm:
                        #print "nebylo 4/4, nahral jsem "
                        return noteMatrix

                elif isinstance(event, midi.NoteEvent):
                    if event.pitch < lowest:
                        lowest = event.pitch
                    if event.pitch > highest:
                        highest = event.pitch

                try:
                    remainingTime[i] = track[pos + 1].tick
                    positionInTrack[i] += 1
                    
                # a bit of a bad practice here, but it's not the main time consuming part of the program
                except IndexError:
                    remainingTime[i] = None

            if remainingTime[i] is not None:
                remainingTime[i] -= 1

        if all(t is None for t in remainingTime):
            break
    return highest, lowest


def main(args):

    highest = lowest = 64 # Initialize for the midi-middle_note
    path = args.dataset

    for name in sorted(os.listdir(path)):
        if name[-4:] in ('.mid', '.MID'):
            pattern = midi.read_midifile(os.path.join(path, name))
            highest, lowest = proccess_pattern(pattern, highest, lowest)

    print(highest)
    print(lowest)


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)
