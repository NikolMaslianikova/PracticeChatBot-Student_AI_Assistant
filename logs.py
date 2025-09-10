import os
import json
import hashlib
import datetime
from pathlib import Path
import aiofiles

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_SALT = os.getenv("LOG_SALT", "unknown")

def _log_file_path(dt: datetime.datetime | None = None) -> Path:
    dt = dt or datetime.datetime.now()
    return LOG_DIR / f"{dt.strftime('%Y-%m-%d')}.jsonl"

def _now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")

def _anon_user_id(uid: int) -> str:
    return hashlib.sha256(f"{uid}{LOG_SALT}".encode()).hexdigest()[:12]

async def log_event(event: dict):
    path = _log_file_path()
    async with aiofiles.open(path, "a", encoding="utf-8") as f:
        await f.write(json.dumps(event, ensure_ascii=False) + "\n")


async def log_user_message(uid: int, message: str, context: dict):
    await log_event({
        "type": "user_message",
        "timestamp": _now_iso(),
        "user": _anon_user_id(uid),
        "message": message,
        **context
    })

async def log_bot_answer(uid: int, message: str, context: dict):
    await log_event({
        "type": "bot_answer",
        "timestamp": _now_iso(),
        "user": _anon_user_id(uid),
        "answer": message,
        **context
    })

async def log_error(uid: int, error: str, context: dict):
    await log_event({
        "type": "error",
        "timestamp": _now_iso(),
        "user": _anon_user_id(uid),
        "error": error,
        **context
    })