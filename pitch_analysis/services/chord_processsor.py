import librosa 
import numpy as np 
import pandas as pd 
import note_process 
from key_scales import key_scales

class Chord_processor:
    def __init__(self, detected_key):
        self.detected_key = detected_key 

    def sort_by_note_position(self,triad, note):
        return triad.index(note)
    
    def generate_chords(self):
        key_notes = key_scales.get(self.detected_key )
        length = len(key_notes)
        triad_chords = []
        for i in range(length):
            triad_chords.append([key_notes[i % length], key_notes[(i + 2) % length], key_notes[(i + 4) % length]])
        return triad_chords 
    
    

    