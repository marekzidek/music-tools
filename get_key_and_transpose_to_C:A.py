import music21


###### Over si tady ten score analyzer, jestli bude moct vratit treba F-3 misto F, 
###### tzn. pouzij takovej ten svuj skript na transpozici dat, jestli ho mas


# p.getPitchRanges(s) m vrati to, na co jsem si psal skript... :D

C4 = 60
A4 = 69

def compute_average_pitch(pattern, highest, lowest):

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


score = music21.converter.parse('filename.mid')
key = score.analyze('key')

# Name = F, mode = minor
print(key.tonic.name, key.mode)




# Should be chromatic interval
bInterval = interval.notesToChromatic(aPitch, bPitch)

i = interval.Interval(k.tonic, pitch.Pitch('C-1'))
sNew = s.transpose(i)

## Transpose to A or C ##

if key.mode = "minor":
	pass
else
	pass