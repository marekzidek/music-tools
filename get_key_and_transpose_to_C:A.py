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

def assume_octave_of_key(pattern, key_list):
    proximity = compute_average_pitch(pattern)[0]

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



c_proximity_list = [48, 60, 72, 84, 96]
a_proximity_list = [57, 69, 81, 93, 105]

def transpose_to_C_or_A(score):

    k = score.analyze('key')

    ## Transpose to A or C ##
    
    if k.mode == "minor":

        k.tonic.octave = k.tonic.implicitOctave
        a = pitch.Pitch('A')
        a.octave = a.implicitOctave
        i = interval.Interval(k.tonic, a)
        sNew = score.transpose(i)

        a_pitch = pitch.Pitch('A')
        a_pitch.midi = assume_octave_of_key(sNew, a_proximity_list)

        i = interval.Interval(a_pitch, a)
        final = sNew.transpose(i) 

    elif k.mode == "major":
        
        k.tonic.octave = k.tonic.implicitOctave
        c = pitch.Pitch('C')
        c.octave = c.implicitOctave
        i = interval.Interval(k.tonic, c)
        sNew = score.transpose(i)

        c_pitch = pitch.Pitch('C4')
        c_pitch.midi = assume_octave_of_key(sNew, c_proximity_list)

        i = interval.Interval(c_pitch, c)
        final = sNew.transpose(i)

    return final

def main(args):

    path = args.dataset

    for name in sorted(os.listdir(path)):
        if name[-4:] in ('.mid', '.MID'):
            score = music21.converter.parse(os.path.join(path, name))

            transposed = transpose_to_C_or_A(score)
            transposed.write("midi", "transposed_" + name)
            
            #score.write("midi", "identity_" + name)


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)




	