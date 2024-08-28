# JazzFlow.py
#
# This program takes MIDI files, diatonically transposes the pieces through scales, 
# and writes new MIDI files.

from music import *
from gui import *
from java.io import File

# scales of chords by "pitch class", semitones are assigned to 0-11 
MAJOR_SIXTH_AND_DIMINISHED                    = (0, 2, 4, 5, 7, 8, 9, 11)                                                          
MINOR_SIXTH_AND_DIMINISHED                    = (0, 2, 3, 5, 7, 8, 9, 11)
DOMINANT_SEVENTH_AND_DIMINISHED               = (0, 2, 4, 5, 7, 8, 10, 11)
DOMINANT_SEVENTH_FLAT_FIVE_AND_DIMINISHED     = (0, 2, 4, 5, 6, 8, 10, 11)
DIMINISHED_AND_THE_ROOTS_OF_ITS_DOMINANTS     = (0, 2, 3, 5, 6, 8, 9, 11) # whole-half diminished scale
DIMINISHED_AND_THE_FIFTHS_OF_ITS_MINOR_SIXTHS = (0, 1, 3, 4, 6, 7, 9, 10) # half-whole diminished scale
WHOLE_TONE                                    = (0, 2, 4, 6, 8, 10)
allScalesList = [MAJOR_SIXTH_AND_DIMINISHED, MINOR_SIXTH_AND_DIMINISHED, 
                DOMINANT_SEVENTH_AND_DIMINISHED, DOMINANT_SEVENTH_FLAT_FIVE_AND_DIMINISHED]

# USEFUL REDUNDANT SCALES, a.k.a modes
# the "Major-Sixth and Diminished" scale with the sixth in the bass 
MINOR_SEVENTH_AND_DIMINISHED = (0, 2, 3, 5, 7, 8, 10, 11)
# the "Minor-Sixth and Diminished" scale with the sixth in the bass
MINOR_SEVENTH_FLAT_FIVE_AND_DIMINISHED = (0, 2, 3, 5, 6, 8, 10, 11)


# useful dictionaries
halfStepLocations = {
    MAJOR_SIXTH_AND_DIMINISHED: [2, 4, 5, 7],
    MINOR_SIXTH_AND_DIMINISHED: [1, 4, 5, 7],
    DOMINANT_SEVENTH_AND_DIMINISHED: [2, 4, 6, 7],
    DOMINANT_SEVENTH_FLAT_FIVE_AND_DIMINISHED: [2, 3, 6, 7],
    DIMINISHED_AND_THE_ROOTS_OF_ITS_DOMINANTS: [1, 3, 5, 7],
    DIMINISHED_AND_THE_FIFTHS_OF_ITS_MINOR_SIXTHS: [0, 2, 4, 6]
}

scaleFileEndings = {
    MAJOR_SIXTH_AND_DIMINISHED: "maj6",
    MINOR_SIXTH_AND_DIMINISHED: "min6",
    DOMINANT_SEVENTH_AND_DIMINISHED: "dom7",
    DOMINANT_SEVENTH_FLAT_FIVE_AND_DIMINISHED: "d7b5",
    DIMINISHED_AND_THE_ROOTS_OF_ITS_DOMINANTS: "hwhw",
    DIMINISHED_AND_THE_FIFTHS_OF_ITS_MINOR_SIXTHS: "whwh",
    WHOLE_TONE: "wwww"
}

noteDropDownMapping = {
    "C": 0,
    "C#/Db": 1,
    "D": 2,
    "D#/Eb": 3,
    "E": 4,
    "F": 5,
    "F#/Gb": 6,
    "G": 7,
    "G#/Ab": 8,
    "A": 9,
    "A#/Bb": 10,
    "B": 11
}

scaleDropDownMapping = {
    "Maj6 + Diminished": MAJOR_SIXTH_AND_DIMINISHED,
    "Min6 + Diminished": MINOR_SIXTH_AND_DIMINISHED,
    "Dom7 + Diminished": DOMINANT_SEVENTH_AND_DIMINISHED,
    "Dom7 b5 + Diminished": DOMINANT_SEVENTH_FLAT_FIVE_AND_DIMINISHED
}


##########################################
# functions

# list pieces: MIDI file names as Strings
# int rootNote: the root note of the desired scale
# list scaleOfChords: the desired scale to tranpose through
# int diatonicTranspositionAmount: how many scale degrees should each note move?
# returns nothing, writes MIDI files
def writeDiatonicTranspositionFile( pieces, rootNote, scale, diatonicTranspositionAmount ):
    """Reads MIDI files to Scores. Diatonically transposes those Scores and writes new MIDI files."""

    # read MIDI files
    for piece in pieces:
        # read this MIDI file into a score
        score = Score() # create an empty score
        Read.midi( score, piece ) # read MIDI file into score

        # transpose the score as many degrees as desired
        diatonicallyTransposeScore( score, rootNote, scale, diatonicTranspositionAmount )
        
        # write a new MIDI file
        newFileName = piece[:-4] + "_transp" + str(diatonicTranspositionAmount) + ".mid"
        Write.midi( score, newFileName )
    

    # now, all the MIDI files have been read into dictionary
    print() # output one more newline


def diatonicallyTransposeScore( score, rootNote, scale, diatonicTranspositionAmount ):
    """Moves every note in a Score up the desired number of scale degrees."""
    for part in score.getPartList(): # for every part in score
        for phrase in part.getPhraseList(): # for every phrase in part
            noteList = phrase.getNoteList()
            for i in range(len(noteList)): # for every note in phrase
                note = noteList[i]

                for i in range(diatonicTranspositionAmount):
                    pitchClass  = (note.getPitch() - rootNote) % 12
                    
                    # if a note is out of the scale, move it up a semitone
                    if pitchClass not in scale: 
                        # print("pitch class out of scale: " + str(pitchClass))
                        Mod.transpose( note, 1 )
                    
                    # otherwise, transpose the note the appropriate amount of semitones       
                    else:
                        scaleIndex = scale.index(pitchClass)
                        semitones = getTranspositionSemitones( scaleIndex, scale )
                        Mod.transpose( note, semitones )


def getTranspositionSemitones( scaleIndex, scale ):
    """Returns the appropriate amount of semitones to transpose, 
    depending on the scale degree and scale.""" 
    global halfStepLocations

    halfStepsList = halfStepLocations.get(scale, [-1]) # get the locations

    if scaleIndex in halfStepsList: return 1 # a half step transposition is needed
    else: return 2 # a whole step transposition is needed


def writeQuantizedFiles( pieces, rootNote, scale ):
    """Normalizes all notes in a MIDI file to fit a scale. 
    Writes a new MIDI file. Returns a list of the new file names."""
    global scaleFileEndings
    
    quantizedMIDIFiles = [] # a list of the newly written files
    quantum = 0.1 # how strict the quantize is
    fileNameEnding = "" # an ending to distinguish the scale

    fileNameEnding = scaleFileEndings.get(scale) 

    if fileNameEnding is None:
        # Handle the case where the scale is not in the dictionary (optional)
        print("WARNING: Unrecognized scale. Using empty string for filename ending.")
        fileNameEnding = ""

    for piece in pieces:
        # read this MIDI file into a score
        score = Score() # create an empty score
        Read.midi( score, piece ) # read MIDI file into score

        quantizeMidiFilesToScale( pieces, rootNote, scale, score )
                
        # write a new MIDI file
        if piece[-8:-4] in ['maj6', 'min6', 'dom7', 'd7b5', 'hwhw', 'whwh', 'wwww']:
            newFileName = piece[:-9] + "_" + fileNameEnding + ".mid"
        else: 
            newFileName = piece[:-4] + "_" + fileNameEnding + ".mid"
        
        Write.midi( score, newFileName )
        quantizedMIDIFiles.append( newFileName )
    
    return quantizedMIDIFiles


def quantizeMidiFilesToScale( pieces, rootNote, scale, score ):
    for part in score.getPartList(): # for every part in score
        for phrase in part.getPhraseList(): # for every phrase in part
            noteList = phrase.getNoteList()
            for i in range(len(noteList)): # for every note in phrase
                note = noteList[i]
                pitchClass  = (note.getPitch() - rootNote) % 12

                if scale == MAJOR_SIXTH_AND_DIMINISHED:
                    if pitchClass in [1, 3, 6, 10]: 
                        Mod.transpose( note, 1 ) # up a half step

                elif scale == MINOR_SIXTH_AND_DIMINISHED:               
                        if pitchClass in [1, 6, 10]: 
                            Mod.transpose( note, 1 ) # up a half step
                        elif pitchClass in [4]: 
                            Mod.transpose( note, -1 ) # down a half step
                
                elif scale == DOMINANT_SEVENTH_AND_DIMINISHED:                  
                    if pitchClass in [1, 3, 6, 9]: 
                        Mod.transpose( note, 1 ) # up a half step

                elif scale == DOMINANT_SEVENTH_FLAT_FIVE_AND_DIMINISHED:                 
                    if pitchClass in [1, 3, 9]: 
                        Mod.transpose( note, 1 ) # up a half step
                    elif pitchClass == 7:
                        Mod.transpose( note, -1 ) # down a half step


def generateAllDiatonicTranspositions( pieces, rootNote, scale ):
    """ Produces MIDI files for all 7 sequences """
    for diatonicTranspositionAmount in range(1, 8):
        writeDiatonicTranspositionFile( pieces, rootNote, scale, diatonicTranspositionAmount )


def generateAllDiatonicTranspositionsForAllScales( pieces, rootNote ):
    global allScalesList    
    quantizedMIDIFiles = []
    
    for scale in allScalesList:
        quantizedMIDIFiles = writeQuantizedFiles( pieces, rootNote, scale )
        generateAllDiatonicTranspositions( quantizedMIDIFiles, rootNote, scale )



###########################
# choose your parameters
midiFiles = [] # list of MIDI files to analyze, include .mid
rootNote = G_1 #0-11, or C_1 to B_1
scale = MINOR_SIXTH_AND_DIMINISHED # any scale
diatonicTranspositionAmount = 0 # number of scale degrees to move all notes

########################### 
# call functions
# quantizedMIDIFiles = writeQuantizedFiles( midiFiles, rootNote, scale )
# generateDiatonicTransposition( midiFiles, rootNote, scale, diatonicTranspositionAmount )
# generateAllDiatonicTranspositions( midiFiles, rootNote, scale )
# generateAllDiatonicTranspositionsForAllScales( midiFiles, rootNote )


###########################
# GUI helper functions
def scaleSelected( selectedScale ):
    """Handles the scale drop down list."""
    global scale
    global scaleDropDownMapping

    # Use get() with a default value to handle invalid selections (optional)
    scale = scaleDropDownMapping.get(selectedScale, None)  


def rootNoteSelected( selectedRoot ):
    """Handles the root note drop down list."""
    global rootNote
    global noteDropDownMapping

    rootNote = noteDropDownMapping.get(selectedRoot, None)  # Handle invalid roots

def processFileName(fileName):
    global midiFiles

    try:
        # Check if file exists with provided filename
        fileObj = File(fileName)
        if fileObj.exists():
            with open(fileName, "r") as f:
                data = f.read()
                print("\n\nMIDI file added.")
                midiFiles.append(fileName)
                print("List of MIDI files: " + str(midiFiles))
        else:
            # Check if file exists without quotes
            noQuotesName = fileName.strip('"')
            fileObj = File(noQuotesName)
            # Check if file exists with ".mid" extension
            midFileName = fileName + ".mid"
            fileObj2 = File(midFileName)
            if fileObj.exists():
                with open(noQuotesName, "r") as f:
                    data = f.read()
                    print("\n\nMIDI file added.")
                    midiFiles.append(noQuotesName)
                    print("The MIDI file: " + str(midiFiles))
            elif fileObj2.exists():
                with open(midFileName, "r") as f:
                    data = f.read()
                    print("\n\nMIDI file added.")
                    midiFiles.append(midFileName)
                    print("The MIDI file: " + str(midiFiles))
            else:
                print("File not found. Try again or provide the full path to the MIDI file.")
    except Exception as e:
        print("An error occurred: ", e)


def allTranspositionsButtonPressed():
    global rootNote
    global scale
    global midiFiles
    generateAllDiatonicTranspositions( midiFiles, rootNote, scale )

def allScalesButtonPressed():
    global rootNote
    global midiFiles

    generateAllDiatonicTranspositionsForAllScales( midiFiles, rootNote )


##########################
# create the GUI
display = Display( "JazzFLow" )   

fileTextField = TextField( "Type a MIDI file in the same directory as this program. Hit <ENTER>.", 42, processFileName )
display.add( fileTextField, 100, 50 )

# scale dropdown
scaleLabel = Label( "Select a \"scale of chords\": " )
display.add( scaleLabel, 25, 100 )
scaleDropDown = DropDownList( ["Maj6 and Diminished", "Min6 and Diminished", "Dom7 and Diminished", 
                            "Dom7b5 and Diminished"], scaleSelected )
display.add( scaleDropDown, 200, 100 )

# root note dropdown
rootNoteLabel = Label("Select a root note: ")
display.add(rootNoteLabel, 25, 150)
rootNoteDropDown = DropDownList( ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", 
                                "G", "G#/Ab", "A", "A#/Bb", "B"], rootNoteSelected )
display.add(rootNoteDropDown, 200, 150)

# button
allTranspositionsButton = Button( "Write 7 Diatonic Transpositions using the Selected Scale", allTranspositionsButtonPressed )
display.add(allTranspositionsButton, 150, 200 )

# button
allScalesButton = Button( "Write All Diatonic Transpositions for All Scales", allScalesButtonPressed )
display.add(allScalesButton, 150, 250 )

display.showMouseCoordinates()