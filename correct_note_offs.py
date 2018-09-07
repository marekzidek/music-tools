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

def correct(midifile):
    pattern = midi.read_midifile(midifile)

    new_step = False
    for track in pattern:
        steps = 1
        
        for i, event in enumerate(track):

            if event.tick > 0:
                reorganize(i, steps, track)
                steps = 1
            else:
                steps += 1

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


        pattern = correct(os.path.join(args.i, file))

        filename = os.path.join(args.o, file)

        if not filename.endswith('mid'):
            if not filename.endswith('midi'):
                filename += '.mid'

        midi.write_midifile(filename, pattern)

