import librosa 
import numpy as np 
import pandas as pd 

class Time_quantization: 
    def __init__(self, tempo, onset_times):
        self.onset_times = onset_times
        self.tempo = tempo 
        beat_per_sec = tempo/60
        second_per_beat = 60/tempo
        grids_per_beat = 4
        seconds_per_grid = (second_per_beat/grids_per_beat)
        # msec_per_grid = (second_per_beat/grids_per_beat)*1000
        corrected_start_time_grid = [round(x/seconds_per_grid) for x in onset_times]
        duplicates = [i for i, x in enumerate(corrected_start_time_grid) if corrected_start_time_grid.count(x) > 1]
        index_to_change_new = [duplicates[i] for i in range(len(duplicates)) if i%2!=0]


    def time_quantize(self):
        for x in self.index_to_change_new:
            runnig_index = x
            while runnig_index>=0:

                if self.corrected_start_time_grid[runnig_index] == self.corrected_start_time_grid[runnig_index-1] and self.corrected_start_time_grid[runnig_index-1]!=0:
                    self.corrected_start_time_grid[runnig_index-1] = self.corrected_start_time_grid[runnig_index-1]-1
                    runnig_index = runnig_index-1

                else:
                    break;


        something = [i for i,x in enumerate(self.corrected_start_time_grid) if x == 0]


        for s in something[::-1]:
            if s==0:
                break;
            for i in range(s, len(self.corrected_start_time_grid)):
                self.corrected_start_time_grid[i] += 1


        corrected_start_time = [x*self.seconds_per_grid for x in self.corrected_start_time_grid]
        corrected_start_time_beat = [x * self.beat_per_sec for x in corrected_start_time]
        duration_in_second = [self.onset_times[i]-self.onset_times[i-1] for i in range(1,len(self.onset_times))]
        corrected_start_time_beat.pop()


        for i in range(len(corrected_start_time)-1):
            if corrected_start_time[i] + duration_in_second[i] > corrected_start_time[i+1]:
                duration_in_second[i] =  corrected_start_time[i+1] - corrected_start_time[i]

        duration_beat_trunc = [x * self.beats_per_sec for x in duration_in_second]




