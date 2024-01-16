import os
import random
import string
from typing import List, Optional, Union
import numpy as np
import aiofiles
from fastapi import File, UploadFile, status
from fastapi.responses import JSONResponse
from midiutil.MidiFile import MIDIFile
from basic_pitch.inference import predict_and_save
from load_dotenv import load_dotenv
from audio_to_midi.crud.file_info_dal import get_file_dal
from audio_to_midi.services.file_service import FileService
from audio_to_midi.schemas.file_schemas import FileCreate, FileUpdate
from audio_to_midi.schemas.pitch_schemas import PitchData, PitchInfo
from user_acc.app import User
from pitch_analysis.services.audio_process import Process
import librosa 

load_dotenv()


class MidiGenerator:
    def __init__(
        self,
        user: User,
        tempo=72,
        volume=100,
        track=0,
        channel=0,
        time_signature=(4, 4),
    ):
        self.tempo, self.volume, self.track, self.channel, self.time_signature = (
            tempo,
            volume,
            track,
            channel,
            time_signature,
        )
        self.elapsed_time = 0
        self.track_counter = 0
        self.midi_obj = MIDIFile(1)
        self.user = user
        self._get_path_of_user()

    def _get_path_of_user(self):
        base_dir = os.getenv("AMT_UPLOAD_DIR", "/home/mir/amt_backend/amt_uploads")
        self.user_dir = os.path.join(
            base_dir,
            f"{self.user.name}_{str(self.user.id)[-4:]}",
        )

    def _random_name(
        self,
        allowed_chars: Optional[str] = string.ascii_letters,
        length: Optional[int] = 6,
    ):
        if not allowed_chars:
            allowed_chars = string.ascii_letters + string.digits
        return "".join(random.choice(allowed_chars) for x in range(length))

    def create_midi_from_pitch(
        self,
        pitch_data: List[PitchData],
        base_time: Optional[float] = None,
        name: Optional[str] = None,
    ):
        self.track_counter += 1
        base_time = base_time if base_time else self.elapsed_time
        track_name = self._random_name() + ".mid"
        self.midi_obj.addTrackName(self.track, self.elapsed_time, track_name)
        self.midi_obj.addTempo(self.track, self.elapsed_time, self.tempo)

        for pitch in pitch_data:
            pitch_value = pitch.pitch
            # last_end_time = 0
            data = pitch.data
            for info in data:
                volume = info.volume if info.volume else self.volume
                channel = info.channel if info.channel else self.channel
                track = info.track if info.track else self.track
                # last_end_time = last_end_time+info.duration if not info.start_time else info.start_time+info.duration
                self.elapsed_time = (
                    info.start_time + info.duration
                    if info.start_time + info.duration > self.elapsed_time
                    else self.elapsed_time
                )
                self.midi_obj.addNote(
                    track,
                    channel,
                    pitch_value,
                    info.start_time,
                    info.duration,
                    volume,
                )

    def create_midi_from_notes(
        self,
        degrees: List[int],
        start_times_beat: List[np.float64],
        duration_in_beat: List[np.float64],
        volume: List[int],
        name: Optional[str] = None,
        beat: Optional[float] = None,
        tempo: Optional[int] = 22,
    ):
        self.track_counter += 1
        track_name = self._random_name() + ".mid"
        self.midi_obj.addTrackName(self.track, self.elapsed_time, track_name)
        if beat:
            self.midi_obj.addTempo(self.track, self.elapsed_time, beat)

        self.midi_obj.addTempo(
            self.track, self.elapsed_time, tempo=beat
        )  # need_optimization

        for pitch, time, duration, vol in zip(
            degrees, start_times_beat, duration_in_beat, volume
        ):
            self.midi_obj.addNote(self.track, self.channel, pitch, time, duration, vol)
        return self.midi_obj

    async def _save_file_record(self, complete_path):
        file_service = FileService(user=self.user)
        file_path = os.path.dirname(complete_path)
        file_name = os.path.basename(complete_path)
        file_info = FileCreate(
            file_name=file_name,
            file_path=file_path,
            user_id=self.user.id,
        )
        try:
            resp = await file_service.create(file_info)
            return resp
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "File record creation error",
                    "error": str(e),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def save_audio(
        self,
        file: UploadFile,
        name: Union[str, None] = None,
    ):
        extension = os.path.splitext(file.filename)[1]
        extension = extension.replace(".", "")
        name = os.path.splitext(file.filename)[0] if not name else name
        complete_path = os.path.join(
            self.user_dir,
            f"{name}.{extension}",
        )
        if os.path.exists(complete_path):
            return JSONResponse(
                content={
                    "message": "this file already exists. Please change file name"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)

        print(complete_path)

        async with aiofiles.open(complete_path, "wb") as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        try:
            resp = await self._save_file_record(complete_path=complete_path)
            return resp
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "File record saving error",
                    "error": str(e),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def save_midi(self, name: Optional[str] = None):
        # Write the MIDI file to disk
        track_name = self._random_name() if not name else name
        file_name = f"{track_name}.mid"
        if not self.user_dir:
            self._get_path_of_user()
        complete_path = os.path.join(
            self.user_dir,
            file_name,
        )
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        resp = await self._save_file_record(complete_path=complete_path)

        if isinstance(resp, JSONResponse):
            return resp
        with open(complete_path, "wb") as file:
            self.midi_obj.writeFile(file)
        return resp

    def audio_to_midi_bp(self, audio_path_list: List[str]):
        if not self.user_dir:
            self._get_path_of_user()
        try:
            predict_and_save(
                audio_path_list=audio_path_list,
                output_directory=self.user_dir,
                save_midi=True,  # midi file
                sonify_midi=False,  # synthesized audible midi file (converted to wav)
                save_model_outputs=False,  # .npz file with digital embedding
                save_notes=True,
                model_path="ICASSP_2022_MODEL_PATH",  # this is a pre-trained model developed by Spotify's Audio Intelligence Lab
                onset_threshold=0.5,
                frame_threshold=0.3,
                minimum_note_length=58,
                sonification_samplerate=44100,
                midi_tempo=120,
            )
            return True
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "File record convertion error",
                    "error": str(e),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def audio_to_midi(
        self,
        audio_path: str,
        tempo: Optional[int],
    ):
        if not self.user_dir:
            self._get_path_of_user()
        complete_path = os.path.join(
            self.user_dir,
            audio_path,
        )
        try:
            y, sr = librosa.load(complete_path, sr=None)
            if not tempo:
                tempo = int(librosa.beat.tempo(sr=sr))

            proc = Process(y=y, sr=sr)
            (
                degrees,
                beats_per_sec,
                start_times_beat,
                duration_in_beat,
                norm_vol,
                beat,
            ) = proc.construct_default()
            self.midi_obj = self.create_midi_from_notes(
                degrees=degrees,
                start_times_beat=start_times_beat,
                duration_in_beat=duration_in_beat,
                volume=norm_vol,
                beat=beat,
                tempo=tempo,
            )

            # self.save_midi(name=name)
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "File record retrival error",
                    "error": str(e),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
