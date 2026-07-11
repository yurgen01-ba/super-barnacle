from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol

@dataclass(slots=True)
class WordTimestamp:
    word:str
    start:float|None
    end:float|None
    score:float|None=None
    speaker:str|None=None

@dataclass(slots=True)
class TranscriptSegment:
    id:int
    start:float
    end:float
    text:str
    speaker:str|None=None
    words:list[WordTimestamp]=field(default_factory=list)
    confidence:float|None=None

@dataclass(slots=True)
class AudioTranscriptionResult:
    text:str
    language:str
    segments:list[TranscriptSegment]
    backend:str
    model:str
    runtime:dict
    warnings:list[str]=field(default_factory=list)

    def to_dict(self)->dict:
        return {
            "text":self.text,
            "language":self.language,
            "backend":self.backend,
            "model":self.model,
            "runtime":self.runtime,
            "warnings":list(self.warnings),
            "segments":[{
                "id":s.id,"start":s.start,"end":s.end,"text":s.text,
                "speaker":s.speaker,"confidence":s.confidence,
                "words":[{"word":w.word,"start":w.start,"end":w.end,"score":w.score,"speaker":w.speaker} for w in s.words]
            } for s in self.segments],
        }

class AudioTranscriber(Protocol):
    def transcribe(self,audio_path:str,language:str|None=None,min_speakers:int|None=None,max_speakers:int|None=None)->AudioTranscriptionResult: ...
