from pitch_analysis.utils import key_scales
from typing import Union
import librosa
import numpy as np


class NoteProcess:
    def __init__(
        self, degrees, duration_in_beat, freq, y_notes, beat, onset_times
    ) -> None:
        self.degrees = degrees
        self.duration_in_beat = duration_in_beat
        self.freq = freq
        self.y_notes = y_notes
        self.beat = beat
        self.onset_times = onset_times

    def identify_notes(self):
        notes_by_pitch = {}
        for note, duration in zip(self.degrees, self.duration_in_beat):
            if note in notes_by_pitch:  # finds the unique notes
                notes_by_pitch[note].append(duration)
            else:
                notes_by_pitch[note] = [duration]

        self.unique_notes = list(librosa.midi_to_note(list(notes_by_pitch.keys())))
        # converting the unique notes of the song to midi numbers to identify the lowest note
        self.unique_midi = librosa.note_to_midi(self.unique_notes)

        # sort from smallest to largest
        self.unique_midi.sort()
        # identify occurences
        note_occurences = []
        for key in notes_by_pitch:
            occurences = len(notes_by_pitch[key])
            note_occurences.append(occurences)

        # sort them according to note_occurences
        note_data = list(zip(self.unique_notes, note_occurences))
        self.note_desc = sorted(note_data, key=lambda x: x[1], reverse=True)

        most_common_note = max(notes_by_pitch, key=lambda k: len(notes_by_pitch[k]))
        self.most_occuring_key = librosa.midi_to_note(most_common_note)
        return self.note_desc

    def change_value_list_to_midi(self, value_set):
        return [str(librosa.note_to_midi(x)) for x in value_set]

    def remove_duplicates_preserve_midi_order(self, input_list):
        seen = set()  # Create an empty set to store seen elements
        output_list = (
            []
        )  # Create an empty list to store unique elements while preserving order

        for item in input_list:
            if item not in seen:
                seen.add(item)  # Add the item to the set of seen elements
                output_list.append(
                    str(librosa.note_to_midi(item))
                )  # Add the item to the output list

        return output_list

    def note_loss_func(self, uniq_significat_midi_sets, sorted_midi_data):
        # create a dictionary of scores to observe the notes that come closest to the key
        key_score_dict = {}
        for key in key_scales:
            key_score_dict[key] = 0  # intialize with zero

        for key, value_set in key_scales.items():
            value_list = self.change_value_list_to_midi(value_set)
            uniq_notes_set = set(uniq_significat_midi_sets)
            # dif_from_keys = set(value_list) - uniq_notes_set  #stores values present in value_list not in uniq_notes_set
            dif_in_keys = uniq_notes_set - set(
                value_list
            )  # stores the notes that are in uniq_notes_set not in value_list
            # key_error_score = sum([sorted_midi_data.get(key_def, 0) for key_def in list(dif_from_keys)])  #stores the number of notes that do not appear in the note_data, this is trivial all answers will be 0
            different_midi_error = sum(
                [sorted_midi_data.get(note_def, 0) for note_def in list(dif_in_keys)]
            )  # stores the number of extra notes appearing in the note_data, not in key scale
            key_score_dict[key] = (
                different_midi_error / len(dif_in_keys)
                if not len(dif_in_keys) == 0
                else 0
            )  # on average how often do the extra notes appear in the song that are not in the key scale

        sorted_key_score_dict = {
            k: v for k, v in sorted(key_score_dict.items(), key=lambda item: item[1])
        }
        index = min(sorted_key_score_dict, key=lambda k: sorted_key_score_dict[k])
        min_data = sorted_key_score_dict.get(index)
        keys_with_value = [
            key for key, value in sorted_key_score_dict.items() if value == min_data
        ]
        return keys_with_value

    def find_closest_midi(self, input_number, num_list: Union[list, None] = None):
        if not num_list:
            num_list = self.accepted_midi
        closest_numbers = []
        min_difference = float("inf")

        for num in num_list:
            num = int(num)
            difference = abs(input_number - num)

            if difference < min_difference:
                min_difference = difference
                closest_numbers = [num]
            elif difference == min_difference:
                closest_numbers.append(num)

        return closest_numbers

    def indentify_key(self, note_desc: Union[list, None] = None):
        if not note_desc:
            note_desc = self.note_desc
        min_occurences = 0
        self.note_soup = [note for note in note_desc if note[1] > min_occurences]

        uniq_significat_notes = [note[:-1] for note, occur in self.note_soup]
        self.uniq_significat_midi_sets = self.remove_duplicates_preserve_midi_order(
            uniq_significat_notes
        )

        note_soup_dict = {}
        midi_soup_dict = {}
        for note, count in self.note_soup:
            # Extract the note name without octave
            note_name_without_octave = note[:-1]
            note_soup_dict[note_name_without_octave] = (
                note_soup_dict.get(note_name_without_octave, 0) + count
            )
            midi_soup_dict[str(librosa.note_to_midi(note_name_without_octave))] = (
                midi_soup_dict.get(
                    str(librosa.note_to_midi(note_name_without_octave)), 0
                )
                + count
            )

        # sorted_note_data = {
        #     k: v
        #     for k, v in sorted(
        #         note_soup_dict.items(), key=lambda item: item[1], reverse=True
        #     )
        # }
        # midi numbers
        sorted_midi_data = {
            k: v
            for k, v in sorted(
                midi_soup_dict.items(), key=lambda item: item[1], reverse=True
            )
        }

        keys_with_value = self.note_loss_func(
            uniq_significat_midi_sets=self.uniq_significat_midi_sets,
            sorted_midi_data=sorted_midi_data,
        )

        if not self.unique_midi:
            self.identify_notes()
        sorted_notes = librosa.midi_to_note(self.unique_midi)
        sort_note = [librosa.note_to_midi(note[:-1]) for note in sorted_notes]

        probable_keys = [key_scales[key] for key in keys_with_value]
        probable_midi_keys = [
            list(librosa.note_to_midi(note_list)) for note_list in probable_keys
        ]

        lowest_value = [
            value
            for value in sort_note
            if all(value in sublist for sublist in probable_midi_keys)
        ][0]
        positions = [
            (index, sublist.index(lowest_value))
            for index, sublist in enumerate(probable_midi_keys)
            if lowest_value in sublist
        ]
        min_index = min(
            (index for index, position in positions), key=lambda x: positions[x][1]
        )
        key_val = probable_midi_keys[min_index]
        self.detected_musical_key = [
            key
            for key, value in key_scales.items()
            if list(librosa.note_to_midi(value)) == key_val
        ]
        self.accepted_notes = key_scales.get(self.detected_musical_key[0])
        self.accepted_midi = [str(librosa.note_to_midi(n)) for n in self.accepted_notes]
        self.accepted_midi.sort()

        return self.detected_musical_key[0], self.accepted_midi

    def get_changing_freq(self):
        not_key_note = list(
            set(self.uniq_significat_midi_sets).difference(self.accepted_midi)
        )  # notes in key not in the song
        note_name = [str(librosa.note_to_midi(note[:-1])) for note in self.y_notes]
        index_to_change = [
            np.where(np.array(note_name) == not_key_note[i])[0]
            for i in range(len(not_key_note))
        ]
        indices = np.concatenate(index_to_change)
        indices_sort = np.sort(indices)
        # freq_to_change = [self.freq[index] for index in indices_sort]
        return indices_sort

    def quantize_note(self, note: str, freq=0):
        pure_note = note[:-1]
        pure_scale = note[-1:]
        pure_midi = librosa.note_to_midi(pure_note)
        closest_midis = self.find_closest_midi(pure_midi)
        closest_midi_notes = librosa.midi_to_note(closest_midis)
        result_midis = [c_n[:-1] + pure_scale for c_n in closest_midi_notes]
        result_frequency = [librosa.note_to_hz(midi) for midi in result_midis]
        if freq:
            diff = abs(result_frequency - freq)
            closest = result_frequency[np.where(diff == min(diff))[0][0]]
            return librosa.hz_to_midi(closest)

        return librosa.note_to_midi(result_midis[-1])

    def note_quantization(self):
        degrees = []
        indices_sort = self.get_changing_freq()

        for i, (note, fre) in enumerate(zip(self.y_notes, self.freq)):
            if i in indices_sort:
                closest_key_note = self.quantize_note(note, fre)
            else:
                closest_key_note = self.quantize_note(note)
            degrees.append(closest_key_note)

        if not self.detected_musical_key or self.note_soup:
            self.indentify_key()

        # detected_key = self.detected_musical_key[0]
        # key_note = detected_key.split(" ")[0]

        # key_note_in_soup = None

        # for note, occurence in self.note_soup:
        #     if librosa.note_to_midi(note[:-1]) == librosa.note_to_midi(key_note):
        #         key_note_in_soup = note
        # break  # gets the first note with octave corresponding to key_note

        # #how many octaves below are the quantized notes from the octave detected in the song from the onset
        # difference_in_midi = librosa.note_to_midi(key_note_in_soup)-librosa.note_to_midi(key_note)

        # the quantized notes are now reset to the correct octave
        self.quantized_degrees = [int(round(deg, 1)) for deg in degrees]
        return self.quantized_degrees

    def time_quantization(self):
        beat_per_sec = self.beat / 60
        second_per_beat = 60 / self.beat
        grids_per_beat = 4
        seconds_per_grid = second_per_beat / 4
        msec_per_grid = (second_per_beat / 4) * 1000

        corrected_start_time_grid = [
            round(x / seconds_per_grid) for x in self.onset_times
        ]
        duplicates = [
            i
            for i, x in enumerate(corrected_start_time_grid)
            if corrected_start_time_grid.count(x) > 1
        ]
        index_to_change_new = [
            duplicates[i] for i in range(len(duplicates)) if i % 2 != 0
        ]

        for x in index_to_change_new:
            runnig_index = x
            while runnig_index >= 0:
                if (
                    corrected_start_time_grid[runnig_index]
                    == corrected_start_time_grid[runnig_index - 1]
                    and corrected_start_time_grid[runnig_index - 1] != 0
                ):
                    corrected_start_time_grid[runnig_index - 1] = (
                        corrected_start_time_grid[runnig_index - 1] - 1
                    )
                    runnig_index = runnig_index - 1

                else:
                    break

        # find the positions(index) where the value of the grid is zero
        something = [i for i, x in enumerate(corrected_start_time_grid) if x == 0]

        # increasing the values of the index by an increment of 1 from the index of the last value till the index of the first value
        for s in something[::-1]:
            if s == 0:
                break
        for i in range(s, len(corrected_start_time_grid)):
            corrected_start_time_grid[i] += 1

        # change the grid values to seconds and then beat for midi conversion
        corrected_start_time = [x * seconds_per_grid for x in corrected_start_time_grid]
        corrected_start_time_beat = [x * beat_per_sec for x in corrected_start_time]
        duration_in_second = [
            self.onset_times[i] - self.onset_times[i - 1]
            for i in range(1, len(self.onset_times))
        ]
        corrected_start_time_beat.pop()

        # truncate over-lapping notes
        for i in range(len(corrected_start_time) - 1):
            if (
                corrected_start_time[i] + duration_in_second[i]
                > corrected_start_time[i + 1]
            ):
                duration_in_second[i] = (
                    corrected_start_time[i + 1] - corrected_start_time[i]
                )

        duration_beat_trunc = [x * beat_per_sec for x in duration_in_second]
