import redis.asyncio as redis
import json
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(os.getenv("REDIS_URL"))

    async def set_session(self, key: str, value: dict, expire_seconds: Optional[int] = 3600) -> None:
        await self.redis.set(key, json.dumps(value), ex=expire_seconds)

    async def get_session(self, key: str) -> Optional[dict]:
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def delete_session(self, key: str) -> bool:
        return await self.redis.delete(key) > 0