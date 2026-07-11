from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(slots=True)
class SpeakerTurn:
    start: float
    end: float
    speaker: str

class SpeakerDiarizationService:
    def __init__(self):
        self.token=os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
        self.pipeline=None

    def is_available(self)->bool:
        try:
            import pyannote.audio  # noqa
            return bool(self.token)
        except Exception:
            return False

    def _load(self):
        if self.pipeline is not None: return self.pipeline
        if not self.token: raise RuntimeError("Set HUGGINGFACE_TOKEN or HF_TOKEN.")
        from pyannote.audio import Pipeline
        import torch
        self.pipeline=Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",use_auth_token=self.token)
        if torch.cuda.is_available(): self.pipeline.to(torch.device("cuda"))
        return self.pipeline

    def diarize(self,audio_path:str,min_speakers:int|None=None,max_speakers:int|None=None)->list[SpeakerTurn]:
        kwargs={}
        if min_speakers is not None: kwargs["min_speakers"]=min_speakers
        if max_speakers is not None: kwargs["max_speakers"]=max_speakers
        diarization=self._load()(audio_path,**kwargs)
        return [SpeakerTurn(round(float(t.start),3),round(float(t.end),3),str(s)) for t,_,s in diarization.itertracks(yield_label=True)]

speaker_diarization_service=SpeakerDiarizationService()
