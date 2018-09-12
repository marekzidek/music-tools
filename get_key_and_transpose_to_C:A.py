from __future__ import print_function
import fnmatch
import glob
import datetime
import subprocess
import music21
from music21 import *
import midi
import argparse

import os


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


def assume_octave_of_key(pattern, key_list, interval):
    """Given a pattern, finds the octave of a key that
        the pattern is played in.
        
        Args:
        pattern: loaded midi score to analyze
        key_list: list of referential key-dependent octave pitches
        interval: an interval that should be added to pattern to be in
        respective referential key (for our use case C or A)
        
        Returns:
        The return value. Midi number of a respective key in the found octave
        """
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
    
    if k.mode == "major":
        
        k.tonic.octave = k.tonic.implicitOctave
        
        # Here, we aim to find the interval between C and score key if we take an assumption
        # that they are both in octave 4, however if we transpose score key by that interval,
        # it still stays in its own octave, but C
        c = pitch.Pitch('C')
        c.octave = c.implicitOctave
        
        # Here, inteval is denoted as some musical strings
        # To make it more understandable, use method .cents on the object interval
        i = interval.Interval(k.tonic, c)
        
        #### This is what we would normaly want:
        # sNew = score.transpose(i)
        #### and then find the corresponding octave and normalize into C4
        #### However, we will just remember the interval and add it to the normalizing interval
        
        c_pitch = pitch.Pitch('C4')
        c_pitch.midi = assume_octave_of_key(score, c_proximity_list, i.cents/100)
        
        final_i = interval.Interval(c_pitch, c).cents + i.cents

    elif k.mode == "minor":
        
        # This is basically a duplicate from k.mode major
        # with slight differences
        k.tonic.octave = k.tonic.implicitOctave
        a = pitch.Pitch('A')
        a.octave = a.implicitOctave
        i = interval.Interval(k.tonic, a)
        a_pitch = pitch.Pitch('A4')
        a_pitch.midi = assume_octave_of_key(score, a_proximity_list, i.cents/100)
        final_i = interval.Interval(a_pitch, a).cents + i.cents

    # Constant determined by trial and error with known atonal pieces and known tonal pieces
    if k.tonalCertainty() > 0.800:
        return final_i/100, k.mode
    else:
        return final_i/100, "atonal"


def fast_transpose(file, interval):
    try:
        pattern = midi.read_midifile(file)
    except:
        return None

    remainingTime = [track[0].tick for track in pattern]
    positionInTrack = [0 for track in pattern]

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
                        event.pitch += int(interval)
                    except:
                        print("Error when transposing -> please report a bug in deterining the interval")

                try:
                    remainingTime[i] = track[pos + 1].tick
                    
                    # a bit of a bad practice here, but it's not the main time consuming part of the program
                except IndexError:
                    remainingTime[i] = None
                
                try:
                    positionInTrack[i] += 1
                    
                except IndexError:
                    remainingTime[i] = None

            if remainingTime[i] is not None:
                remainingTime[i] -= 1
            
        if all(t is None for t in remainingTime):
            break

    return pattern

def write_midifile(final_path, contents):
    if not os.path.exists(os.path.split(final_path)[0]):
        os.makedirs(os.path.split(final_path)[0])
    midi.write_midifile(final_path, contents)
    return


def main(args):
    path = args.dataset
    print(path)
    output_path, tail = os.path.split(path)
    
    # this just for detection of trailing '/' in path
    if tail == '':
        output_path, tail = os.path.split(output_path)

    bashCommand = "find {} -type f | sort".format(args.dataset)
    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    output = output.decode('utf-8')
    
            

    with open("{}.log".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")), "w") as log_file:
        for i, name in enumerate(output.split("\n")):
            if os.path.isfile(name):
                if name[-4:] in ('.mid', '.MID'):

                    unprefixed = os.path.relpath(name,args.dataset) 
                    unpostfixed, filename = os.path.split(unprefixed)
                    # Check if already converted
                    if len(glob.glob(os.path.join("normalized", unpostfixed, "*", filename))) > 0:
                        continue 
                    try:
                        print(name)
                        score = music21.converter.parse(name)

                    except:
                        print("music21 library couldn't parse this one")
                        continue

                    semitones, scale = transpose_to_C_or_A(score)
                    transposed = fast_transpose(name, semitones)
                    if transposed is not None:
                        print("writing {}".format(os.path.join(output_path, name)))
                        try:                
                            if scale == "major":
                                final_path = os.path.join("normalized", unpostfixed, "major", filename) 
                                write_midifile(final_path, transposed) 
                            elif scale == "minor":
                                final_path = os.path.join("normalized", unpostfixed, "minor", filename) 
                                write_midifile(final_path, transposed) 
                            else:
                                final_path = os.path.join("normalized", unpostfixed, "atonal", filename) 
                                write_midifile(final_path, transposed) 

                            print(filename, file=log_file)
                        except Exception as e:
                            print(e)
                            print("Use the generated logfiles to determine if you are wasting time!!!")


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    
    main(args)
