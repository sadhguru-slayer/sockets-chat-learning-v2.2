from collections import defaultdict, deque
from datetime import datetime
from fastapi import WebSocket
import json, re
import redis.asyncio as redis
from redis_client import r

class ConnectionManager:
    def __init__(self):
        self.groups: dict[str, dict[str, WebSocket]] = defaultdict(dict)

    def _now(self):
        return datetime.now().strftime("%H:%M:%S")

    async def connect(self, group_id: str, client_id: str, ws: WebSocket):
        await ws.accept()
        if client_id in self.groups[group_id]:
            await ws.send_json({
                "type": "error",
                "message": "Username already taken"
            })
    
            await ws.close(code=4000)
    
            return False
        self.groups[group_id][client_id] = ws

        # Load previous messages
        history = await r.lrange(f"group:{group_id}:history", -50, -1)

        for msg in history:
            await ws.send_json(json.loads(msg))
        # Create a joined message
        join_msg = {
            "type": "system",
            "event": "join",
            "user": client_id,
            "time": self._now(),
            "message": f"{client_id} joined {group_id}"
        }

        # Broadcast join message
        await self.broadcast(group_id, join_msg)

        await self.send_online_users(group_id)

    async def disconnect(self, group_id: str, client_id: str, ws: WebSocket):

        if client_id in self.groups[group_id]:
            del self.groups[group_id][client_id]

        # Create leave message
        leave_msg = {
            "type": "system",
            "event": "leave",
            "user": client_id,
            "time": self._now(),
            "message": f"{client_id} left {group_id}"
        }

        if not self.groups[group_id]:
            del self.groups[group_id]

        await self.broadcast(group_id, leave_msg)
        await self.send_online_users(group_id)

    async def send_personal_message(self, ws: WebSocket, data: dict):
        # Here the message will be sent to ourself
        await ws.send_json(data)

    async def broadcast(self, group_id: str, data: dict):

        dead = []

        await r.lpush(
            f"group:{group_id}:history",
            json.dumps(data)
        )

        await r.ltrim(
            f"group:{group_id}:history",
            0,
            49
        )

        for username, ws in list(self.groups[group_id].items()):
            try:
                await ws.send_json(data)

            except Exception:
                dead.append(username)

        # Cleanup dead users
        for username in dead:
            del self.groups[group_id][username]

    async def send_online_users(self,group_id:str):
        users = list(self.groups[group_id].keys())
        payload = {
            "type": "online_users",
            "users": users
        }

        if group_id not in self.groups:
            return

        for username, ws in self.groups[group_id].items():
            try:
                await ws.send_json(payload)
            except:
                pass
    