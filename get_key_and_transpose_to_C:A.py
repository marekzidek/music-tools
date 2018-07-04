from __future__ import print_function

import music21
from music21 import *
import midi
import argparse

import os


###### Over si tady ten score analyzer, jestli bude moct vratit treba F-3 misto F, 
###### tzn. pouzij takovej ten svuj skript na transpozici dat, jestli ho mas


REFERENTIAL_C = 72
REFERENTIAL_A = 81


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


def compute_average_pitch(pattern):

    fe = music21.features.jSymbolic.PrimaryRegisterFeature(pattern)
    
    return fe.extract().vector

# (pattern, [options of octaves in midi nunmbers], interval -
# for which we need to move the pattern to be in C or A in some octave)
def assume_octave_of_key(pattern, key_list, interval):
    proximity = compute_average_pitch(pattern)[0] + interval

    # No need for modified binary search
    for a, b in zip(key_list, key_list[1:]):
        if proximity < a:
            proximity = a
            break
        if proximity > b:
            continue
        if proximity < b and proximity > a:
            proximity = a if (proximity - a) < (b - proximity) else b
            break
    else:
        proximity = key_list[-1]

    return proximity



c_proximity_list = [36, 48, 60, 72, 84, 96, 108]
a_proximity_list = [33, 45, 57, 69, 81, 93, 105]

def transpose_to_C_or_A(score):

    k = score.analyze('key')

    ## Transpose to A4 or C4 ##
    
    elif k.mode == "major":

        k.tonic.octave = k.tonic.implicitOctave

        # Here, we aim to find the interval between C and score key if we take an assumption
        # that they are both in octave 4, however if we transpose score key by that interval,
        # it still stays in its own octave, but C
        c = pitch.Pitch('C')
        c.octave = c.implicitOctave

        # Here, inteval is denoted as some musical strings
        # To make it more understandable, use method .cents on the object interval
        i = interval.Interval(k.tonic, c)

        #### keep the next line commented: This is what we would normaly want
        # sNew = score.transpose(i)
        #### and then find the corresponding octave and normalize into C4
        #### However, we will just remember the interval and add it to the normalizing interval

        c_pitch = pitch.Pitch('C4')
        c_pitch.midi = assume_octave_of_key(score, c_proximity_list, i.cents/100)

        final_i = interval.Interval(c_pitch, c).cents + i.cents

    if k.mode == "minor":

        # This is basically a duplicate from k.mode major
        # with slight differences
        k.tonic.octave = k.tonic.implicitOctave
        a = pitch.Pitch('A')
        a.octave = a.implicitOctave
        i = interval.Interval(k.tonic, a)
        a_pitch = pitch.Pitch('A4')
        a_pitch.midi = assume_octave_of_key(score, a_proximity_list, i.cents/100)
        final_i = interval.Interval(a_pitch, a).cents + i.cents

    

    return final_i/100

def fast_transpose(file, interval):
    pattern = midi.read_midifile(midifile)
    remainingTime = [track[0].tick for track in pattern]
    positionInTrack = [0 for track in pattern]

    noteMatrix.append(state)

    while not (all(t is None for t in remainingTime)):

        # for all tracks in current tick
        for i in range(len(remainingTime)):
            # for all notes current tick and track
            while remainingTime[i] == 0:

                track = pattern[i]
                pos = positionInTrack[i]

                event = track[pos]
                if isinstance(event, midi.NoteEvent):
                    try:
                        event.pitch += interval
                try:
                    remainingTime[i] = track[pos + 1].tick

                # a bit of a bad practice here, but it's not the main time consuming part of the program
                except IndexError:
                    print("Takovehle bylo icko pri bad practicu cislo 1 ve fast transpose")
                    print(i)
                    remainingTime[i] = None

                try:
                    positionInTrack[i] += 1

                except IndexError:
                    print("Takovehle bylo icko pri bad practicu cislo 2 ve fast transpose")
                    print(i)
                    remainingTime[i] = None

            if remainingTime[i] is not None:
                remainingTime[i] -= 1

        if all(t is None for t in remainingTime):
            break

    return pattern


def main(args):

    path = args.dataset

    for name in sorted(os.listdir(path)):
        if name[-4:] in ('.mid', '.MID'):
            filename = os.path(join(path, name))
            try:
                score = music21.converter.parse(filename)
            except:
                continue
                
            half_tones = transpose_to_C_or_A(score)
            transposed = fast_transpose(filename, half_tones)
            if not filename.endswith('mid'):
                if not filename.endswith('midi'):
                    filename += '.mid'
                    midi.write_midifile(filename, transposed)
            

if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)