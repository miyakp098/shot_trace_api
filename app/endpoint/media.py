import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()

STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "/data/videos")).resolve()
STORAGE_PATH.mkdir(parents=True, exist_ok=True)

@router.post("/ingest/upload", status_code=201)
async def ingest_upload(file: UploadFile = File(...)):
    upload_id = uuid.uuid4().hex
    suffix = Path(file.filename or "").suffix
    target_path = STORAGE_PATH / f"{upload_id}{suffix}"
    tmp_path = target_path.with_suffix(target_path.suffix + ".part")

    written = 0
    try:
        with tmp_path.open("wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                out.write(chunk)
        tmp_path.rename(target_path)
    except Exception as exc:  # pragma: no cover - minimal API, log-worthy
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to save file") from exc

    return {
        "upload_id": upload_id,
        "stored_path": str(target_path),
        "bytes": written,
        "content_type": file.content_type,
    }


@router.get("/ingest/files", status_code=200)
async def list_uploaded_files():
    files = []
    for path in sorted(STORAGE_PATH.glob("*")):
        if not path.is_file():
            continue
        stat = path.stat()
        files.append(
            {
                "name": path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(path),
            }
        )

    return {"count": len(files), "files": files}
