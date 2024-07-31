import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from connection_manager import ConnectionManager
from models import Client
from config import templates

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    client = Client(websocket=websocket, username=username)
    await manager.connect(client)
    await manager.initialize_client_session(client)

    try:
        while True:
            data = await websocket.receive_text()
            manager.append_new_message(data)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        await manager.disconnect(client)
        await manager.broadcast(f"Пользователь {username} покинул плеер!")
    except Exception as e:
        logging.error("Произошла ошибка: %s", e)
        await manager.disconnect(client)
        await manager.broadcast(f"Пользователь {username} покинул плеер из-за ошибки!")


@router.get("/", response_class=HTMLResponse)
async def music_player_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
