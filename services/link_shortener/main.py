import os
from datetime import datetime
from typing import Any, Dict, Optional

import redis
import shortuuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Link Shortener Service", version="0.1.0")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


class LinkCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None


class LinkResponse(BaseModel):
    short_code: str
    original_url: str
    short_url: str
    created_at: datetime


@app.get("/")
async def root() -> dict:
    return {"message": "Link Shortener Service"}


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    try:
        redis_client.ping()
        return {"status": "ok", "service": "link-shortener", "redis": "connected"}
    except Exception:
        return {"status": "error", "service": "link-shortener", "redis": "disconnected"}


@app.post("/shorten", response_model=LinkResponse)
async def shorten_link(link_data: LinkCreate) -> Dict[str, Any]:
    # Generate short code
    if link_data.custom_alias:
        short_code = link_data.custom_alias
        # Check if already exists
        if redis_client.exists(f"link:{short_code}"):
            raise HTTPException(status_code=400, detail="Custom alias already exists")
    else:
        short_code = shortuuid.uuid()[:8]

    link_info = {
        "original_url": link_data.original_url,
        "created_at": datetime.utcnow().isoformat(),
        "click_count": 0,
    }

    redis_client.hset(f"link:{short_code}", mapping=link_info)  # type: ignore[arg-type]
    redis_client.sadd("all_links", short_code)  # For tracking all links

    short_url = f"http://localhost:8001/{short_code}"

    return LinkResponse(
        short_code=short_code,
        original_url=link_data.original_url,
        short_url=short_url,
        created_at=datetime.utcnow(),
    )


@app.get("/{short_code}")
async def redirect_link(short_code: str) -> Dict[Any, Any]:
    link_data = redis_client.hgetall(f"link:{short_code}")

    if not link_data:
        raise HTTPException(status_code=404, detail="Short link not found")

    redis_client.hincrby(f"link:{short_code}", "click_count", 1)

    original_url = link_data["original_url"]
    return {"redirect": original_url}


@app.get("/stats/{short_code}")
async def get_link_stats(short_code: str) -> Dict[Any, Any]:
    link_data = redis_client.hgetall(f"link:{short_code}")

    if not link_data:
        raise HTTPException(status_code=404, detail="Short link not found")

    return {
        "short_code": short_code,
        "original_url": link_data["original_url"],
        "created_at": link_data["created_at"],
        "click_count": int(link_data.get("click_count", 0)),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
