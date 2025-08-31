from typing import Dict

import httpx

from core.settings import settings


async def shorten(url: str) -> str:
    """Вернёт короткую ссылку из сервиса шортенера."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(
                f"{settings.link_shortener_base_url}/shorten",
                json={"original_url": url},
            )
            resp.raise_for_status()
            data: Dict[str, str] = resp.json()
            return data.get("short_url") or url
    except Exception:
        return url  # не ломаем поток, если шортенер не отвечает
