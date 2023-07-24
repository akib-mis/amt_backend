from pydantic import BaseModel
from typing import Optional, List


class PitchInfo(BaseModel):
    start_time: float
    duration: float  # in beats
    volume: Optional[float]
    channel: Optional[int]
    track: Optional[int]


class PitchData(BaseModel):
    pitch: int
    data: List[PitchInfo]
