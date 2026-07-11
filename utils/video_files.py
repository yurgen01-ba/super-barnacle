import tempfile
from pathlib import Path


def save_uploaded_file_to_temp(uploaded_file) -> str:
    tmp_dir = tempfile.mkdtemp(prefix="project_brain_video_")
    safe_name = (uploaded_file.name or "meeting.mp4").replace("/", "_").replace("\\", "_")
    temp_path = Path(tmp_dir) / safe_name

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(temp_path)


def cleanup_file(path: str):
    try:
        file_path = Path(path)
        parent = file_path.parent
        if file_path.exists():
            file_path.unlink()
        try:
            parent.rmdir()
        except OSError:
            pass
    except Exception:
        pass

