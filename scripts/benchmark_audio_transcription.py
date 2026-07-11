from __future__ import annotations
import argparse,json,time
from transcription.audio_transcriber_factory import create_audio_transcriber

def main():
    p=argparse.ArgumentParser()
    p.add_argument("audio_path")
    p.add_argument("--language",default="ru")
    p.add_argument("--min-speakers",type=int,default=2)
    p.add_argument("--max-speakers",type=int,default=6)
    a=p.parse_args()
    t=create_audio_transcriber()
    started=time.time()
    result=t.transcribe(a.audio_path,a.language,a.min_speakers,a.max_speakers)
    payload=result.to_dict()
    print(json.dumps(payload["runtime"],ensure_ascii=False,indent=2))
    print("Wall clock:",round(time.time()-started,3))
    print("Segments:",len(payload["segments"]))
    print("Warnings:",payload["warnings"])
if __name__=="__main__": main()
