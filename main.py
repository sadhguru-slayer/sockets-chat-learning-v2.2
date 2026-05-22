from fastapi import (
                FastAPI, 
                WebSocket, 
                WebSocketDisconnect,
                Query,
                status        
                )
from datetime import datetime
import json
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
from redis_client import r

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get('/')
async def get():
    with open("index.html","r",encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(html)

from manager import ConnectionManager

manager = ConnectionManager()

def channel(group_id: str):
    return f"group:{group_id}"

@app.on_event("startup")
async def startup():
    asyncio.create_task(redis_listener())

@app.websocket('/ws/{group_id}')
async def groupChat(
    ws:WebSocket,
    group_id:str,
    client_id:str = Query(...)
):
    await manager.connect(group_id,client_id,ws)

    try:
        while True:
            data = await ws.receive_json()
            
            type = data.get("type")

            if type == "chat":
                message = data.get("message", "")
                chat_message = {
                    "type": "chat",
                    "user": client_id,
                    "group": group_id,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "message": message
                }
                await r.publish(f"group:{group_id}",json.dumps(chat_message))

            elif type == "typing":
                typing_message = {
                    "type": "typing",
                    "user": client_id,
                    "group": group_id
                }
                await r.publish(f"group:{group_id}", json.dumps(typing_message))
    except WebSocketDisconnect:
        await manager.disconnect(group_id,client_id,ws)

async def redis_listener():
    pubsub = r.pubsub()
    await pubsub.psubscribe("group:*")

    async for message in pubsub.listen():
        print(message["type"],"-------------")
        if message["type"] != "pmessage":
            continue

        raw = message["data"]

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        data = json.loads(raw)
        channel = message["channel"]

        group_id = channel.split(":")[1]

        if manager.groups.get(group_id):
            for ws in list(manager.groups[group_id].values()):
                try:
                    await ws.send_json(data)
                except:
                    pass