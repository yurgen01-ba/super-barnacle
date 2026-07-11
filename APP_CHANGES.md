# Large video support patch

## 1. Copy `.streamlit/config.toml`

Place it in your project root:

```text
project-brain/
  .streamlit/
    config.toml
```

This increases Streamlit upload limit to 600 MB.

## 2. Copy `utils/video_files.py`

Place it here:

```text
project-brain/
  utils/
    video_files.py
```

Also ensure this file exists:

```text
project-brain/
  utils/
    __init__.py
```

If it does not exist, create an empty file.

## 3. Replace `extractors/meeting.py`

Replace your existing file with the included `extractors/meeting.py`.

## 4. Update `requirements.txt`

Make sure it contains:

```txt
streamlit
anthropic
openai-whisper
ffmpeg-python
python-dotenv
pydantic
pypdf
```

`ffmpeg` itself must still be installed in Windows PATH.

## 5. Update `app.py` video block

Use this pattern in your Streamlit UI:

```python
from extractors.meeting import process_meeting_video

uploaded_videos = st.file_uploader(
    "Upload meeting videos",
    type=["mp4", "mov", "mkv"],
    accept_multiple_files=True,
)

segment_minutes = st.slider(
    "Video segment size, minutes",
    min_value=5,
    max_value=60,
    value=30,
    step=5,
)

if st.button("Process Meeting Videos"):
    for video in uploaded_videos:
        st.info(f"Processing video: {video.name}")

        result = process_meeting_video(
            video,
            source=f"meeting_video:{video.name}",
            segment_seconds=segment_minutes * 60,
        )

        if result["warning"]:
            st.warning(result["warning"])

        st.subheader(f"Transcript preview: {video.name}")
        st.text_area(
            "Transcript",
            result["transcript"][:5000],
            height=250,
            key=f"transcript_{video.name}",
        )

        saved = 0

        for item in result["items"]:
            memory.add(KnowledgeItem(**item))
            saved += 1

        st.success(f"Saved {saved} knowledge items from {video.name}")
```

## 6. Restart Streamlit fully

Stop the app with Ctrl+C, then run:

```powershell
python -m streamlit run app.py
```
