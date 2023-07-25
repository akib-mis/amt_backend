import librosa
import numpy as np
import pandas as pd
from typing import Union
import math
import statistics


class Process:
    def __init__(
        self,
        y: np.ndarray,
        sr: int,
        delta: Union[float, None] = 0.05,
        wait: Union[int, None] = 0,
        frame_size_power: Union[int, None] = 10,
        start_bpm: Union[int, None] = 30,
        hop_ratio: Union[float, None] = 0.5,
    ):
        self.y = y
        self.sr = sr
        self.delta = delta
        self.wait = wait
        self.start_bpm = start_bpm
        self.frame_size = 2**frame_size_power
        self.hop_length = int(hop_ratio * self.frame_size)
        # self.tempo = librosa.beat.tempo(y=self.y, sr=self.sr, start_bpm=self.start_bpm)

    def construct_default(self):
        self.harmonic = self.cleaning_audio(y=self.y)
        (
            self.onset_boundaries,
            self.onset_samples,
            self.onset_times,
            self.beat,
        ) = self.onset_detection(harmonic=self.harmonic)
        self.y_pure, self.y_notes, self.y_vol = self.estimate_note_pitch_volume(
            harmonic=self.harmonic, onset_boundaries=self.onset_boundaries
        )
        y_midi_notes = librosa.note_to_midi(self.y_notes)
        median = np.median(y_midi_notes)
        q_y_notes = self.quantize_notes(midi_notes=self.y_notes, median=median)

        degrees = [
            librosa.note_to_midi(note) if note != "0" else 0 for note in q_y_notes
        ]
        beats_per_sec = self.beat[0] / 60
        start_times_beat = [onset * beats_per_sec for onset in self.onset_times]
        duration_in_beat = [
            start_times_beat[i] - start_times_beat[i - 1]
            for i in range(1, len(start_times_beat))
        ]
        start_times_beat.pop()
        norm_vol = [int(vol / max(self.y_vol) * 127) for vol in self.y_vol]
        # deg_quantized = self.quantize_notes(midi_notes=degrees)

        return (
            degrees,
            beats_per_sec,
            start_times_beat,
            duration_in_beat,
            norm_vol,
            self.beat[0],
        )

    def cleaning_audio(self, y: np.ndarray):
        this_y = y
        y_seg_clean = librosa.effects.split(
            y=this_y,
            frame_length=self.frame_size,
            hop_length=self.hop_length,
        )
        y_clean = librosa.effects.remix(y=this_y, intervals=y_seg_clean)
        harmonic, _ = librosa.effects.hpss(y_clean)
        self.harmonic = harmonic
        return self.harmonic

    def onset_detection(self, harmonic: np.ndarray):
        this_harmonic = harmonic
        onset_env = librosa.onset.onset_strength(
            y=this_harmonic, sr=self.sr, hop_length=self.hop_length
        )
        self.onset_samples = librosa.onset.onset_detect(
            y=this_harmonic,
            onset_envelope=onset_env,
            sr=self.sr,
            units="samples",
            hop_length=self.hop_length,
            backtrack=True,
            pre_max=20,
            post_max=20,
            pre_avg=80,
            post_avg=80,
            delta=self.delta,
            wait=self.wait,
        )
        self.onset_boundaries = np.concatenate(
            [self.onset_samples, [len(this_harmonic)]]
        )
        self.onset_times = librosa.samples_to_time(self.onset_boundaries, sr=self.sr)
        # self.beat = librosa.beat.tempo(y=self.y, sr=self.sr, onset_envelope=onset_env)
        self.beat = librosa.beat.tempo(y=self.y, sr=self.sr, start_bpm=self.start_bpm)
        return self.onset_boundaries, self.onset_samples, self.onset_times, self.beat

    def estimate_pitch(self, segment, sr, fmin=50.0, fmax=2000.0):
        # Compute autocorrelation of input segment.
        r = librosa.autocorrelate(segment)

        # Define lower and upper limits for the autocorrelation argmax.
        i_min = sr / fmax
        i_max = sr / fmin
        r[: int(i_min)] = 0
        r[int(i_max) :] = 0

        # Find the location of the maximum autocorrelation.
        i = r.argmax()
        f0 = float(sr) / i
        return f0

    def generate_sine(self, f0, sr, n_duration):
        n = np.arange(n_duration)
        return 0.2 * np.sin(2 * np.pi * f0 * n / float(sr))

    def estimate_vol(self, segment, sr, fmin=50.0, fmax=2000.0):
        vol = librosa.feature.rms(y=segment)
        vol_avg = np.mean(vol)
        return vol_avg

    def estimate_pitch_and_generate_sine(self, x, onset_samples, i, sr):
        n0 = onset_samples[i]
        n1 = onset_samples[i + 1]
        f0 = self.estimate_pitch(x[n0:n1], sr)
        vol = self.estimate_vol(x[n0:n1], sr)
        return self.generate_sine(f0, sr, n1 - n0), librosa.hz_to_note(f0), vol

    def estimate_note_pitch_volume(
        self,
        harmonic: np.ndarray,
        onset_boundaries: np.ndarray,
    ):
        this_harmonic = harmonic
        this_onset_boundaries = onset_boundaries

        # y_pure_ar = []
        # y_notes_ar = []
        # y_vol_ar = []
        # for i in range(len(this_onset_boundaries) - 1):
        #     pure, note, vol = self.estimate_pitch_and_generate_sine(
        #         this_harmonic, this_onset_boundaries, i, sr=self.sr
        #     )
        #     y_pure_ar.append(pure)
        #     y_notes_ar.append(note)
        #     y_vol_ar.append(vol)

        # self.y_pure, self.y_notes, self.y_vol = (
        #     np.concatenate(y_pure_ar),
        #     np.concatenate(y_notes_ar),
        #     np.concatenate(y_vol_ar),
        # )
        self.y_pure = np.concatenate(
            [
                self.estimate_pitch_and_generate_sine(
                    this_harmonic, this_onset_boundaries, i, sr=self.sr
                )[0]
                for i in range(len(this_onset_boundaries) - 1)
            ]
        )
        self.y_notes = [
            self.estimate_pitch_and_generate_sine(
                this_harmonic, this_onset_boundaries, i, sr=self.sr
            )[1]
            for i in range(len(this_onset_boundaries) - 1)
        ]
        self.y_vol = [
            self.estimate_pitch_and_generate_sine(
                this_harmonic, this_onset_boundaries, i, sr=self.sr
            )[2]
            for i in range(len(this_onset_boundaries) - 1)
        ]

        return self.y_pure, self.y_notes, self.y_vol

    def quantize_notes(self, midi_notes: list, median: float):
        upper_limit = int(median + 6)
        lower_limit = int(median - 6)
        octave_range = []
        quantized_note = []
        for i in range(lower_limit, upper_limit):
            octave_range.append(librosa.midi_to_note(i))

        for note in midi_notes:
            note = note[:-1]
            for oct in octave_range:
                if note in oct:
                    quantized_note.append(oct)
                    break
        return quantized_note
