import librosa 
import numpy as np 
import pandas as pd 
from pitch_analysis.services.note_process import NoteProcess 
from pitch_analysis.utils import key_scales
#from time_quantization 


class Chord_processor:
    """ Class that builds the chord progression. """
    def __init__(self, detected_key, most_common_note, quantized_degrees, corrected_start_time_beat, duration_beat_trunc):
        self.detected_key = detected_key 
        self.most_common_note = most_common_note 
        self.quantized_degrees = quantized_degrees
        self.corrected_start_time_beat = corrected_start_time_beat
        self.duration_beat_trunc = duration_beat_trunc

    def sort_by_note_position(self,triad, note):
        return triad.index(note)
    
    def generate_chords_midi(self):
        key_notes = key_scales.get(self.detected_key)
        length = len(key_notes)
        triad_chords = []
        for i in range(length): 
            triad_chords.append([key_notes[i % length], key_notes[(i + 2) % length], key_notes[(i + 4) % length]])
        return triad_chords #these are the key chords
     
    def generate_midi(self): 
        midi_chords =[]
        for chord_list in self.generate_chords_midi():
            cell  = []
            for notes in chord_list:
                cell.append(librosa.note_to_midi(notes))
            midi_chords.append(cell)
        return midi_chords
    
    def quantized_notes(self): 
        quantized_notes = librosa.midi_to_note(self.quantized_degrees)
        return quantized_notes 

    def chord_progession(self):
        chord_prog = []
        chord_duration = [] 
        chord_start = []
        detected_chords = []
        probable_chord = []
        prev_chord = []
        start = 0
    
        chord_octave = int((self.most_common_note)[-1])

        for i,(note, time) in enumerate(zip(self.quantized_notes, self.corrected_start_time_beat)):
            if not detected_chords:
                detected_chords = self.midi_chords
                prev_chord = detected_chords[0] 
                detected_chords = sorted([x for x in detected_chords if librosa.note_to_midi(note[:-1]) in x], key = lambda triad: self.sort_by_note_position(triad, librosa.note_to_midi(note[:-1])))
                probable_chord = detected_chords[0] if detected_chords else None


            if i == len(self.quantized_notes)-1:
                if probable_chord:
                    chord_start.append(self.corrected_start_time_beat[start])
                    chord_duration.append(self.corrected_start_time_beat[i] + self.duration_beat_trunc[-1] - self.corrected_start_time_beat[start])
                    chord_prog.append([librosa.midi_to_note(x)[:-1] + str(chord_octave) for x in probable_chord])
                else:
                    chord_start.append(self.corrected_start_time_beat[start])
                    chord_duration.append(self.corrected_start_time_beat[i]-self.corrected_start_time_beat[start])
                    chord_prog.append([librosa.midi_to_note(x)[:-1] + str(chord_octave) for x in prev_chord])

                    detected_chords = self.midi_chords
                    detected_chords = sorted([x for x in detected_chords if librosa.note_to_midi(note[:-1]) in x], key=lambda triad: self.sort_by_note_position(triad, librosa.note_to_midi(note[:-1])))

                    chord_start.append(self.corrected_start_time_beat[i])
                    chord_duration.append(self.duration_beat_trunc[-1])
                    chord_prog.append([librosa.midi_to_note(x)[:-1]+str(chord_octave) for x in detected_chords[0]])
                    break

                if not probable_chord:
 

                    chord_start.append(self.corrected_start_time_beat[start])
                    chord_duration.append(self.corrected_start_time_beat[i]-self.corrected_start_time_beat[start])

                    
                    start = i
                    chord_prog.append([librosa.midi_to_note(x)[:-1]+str(chord_octave) if x>12 else librosa.midi_to_note(x+12)[:-1]+str(chord_octave) for x in prev_chord])

                
                    detected_chords = self.midi_chords
                    detected_chords = sorted([x for x in detected_chords if librosa.note_to_midi(note[:-1]) in x], key=lambda triad: self.sort_by_note_position(triad, librosa.note_to_midi(note[:-1])))    

                        












    


    

    
    
    
    

    