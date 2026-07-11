from __future__ import annotations
import time, whisper
from config import WHISPER_DEVICE, WHISPER_MODEL_NAME
from transcription.audio_contracts import AudioTranscriptionResult,TranscriptSegment,WordTimestamp

class OpenAIWhisperAdapter:
    def __init__(self):
        self.model=whisper.load_model(WHISPER_MODEL_NAME,device=WHISPER_DEVICE)
    def transcribe(self,audio_path:str,language:str|None=None,min_speakers:int|None=None,max_speakers:int|None=None)->AudioTranscriptionResult:
        started=time.time()
        result=self.model.transcribe(audio_path,language=language,fp16="cuda" in str(self.model.device).lower(),word_timestamps=True)
        segments=[]
        for idx,item in enumerate(result.get("segments") or []):
            words=[WordTimestamp(str(w.get("word") or "").strip(),w.get("start"),w.get("end"),w.get("probability")) for w in item.get("words") or []]
            segments.append(TranscriptSegment(int(item.get("id",idx)),float(item.get("start") or 0),float(item.get("end") or 0),str(item.get("text") or "").strip(),words=words,confidence=item.get("avg_logprob")))
        return AudioTranscriptionResult(str(result.get("text") or "").strip(),str(result.get("language") or language or "unknown"),segments,"openai-whisper",WHISPER_MODEL_NAME,{"device":str(self.model.device),"seconds":round(time.time()-started,3),"alignment":False,"diarization":False},["Legacy backend has no speaker diarization."])
