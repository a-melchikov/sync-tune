from typing import List, Dict, Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    """
    Управление подключениями и обменом сообщениями между клиентами.

    Атрибуты:
    connected_clients (List[Dict[str, Union[WebSocket, str]]]): список подключенных клиентов (объектов WebSocket).
    message_queue (List[str]): очередь сообщений для отправки клиентам.
    """

    def __init__(self):
        self.connected_clients: List[Dict[str, Union[WebSocket, str]]] = []
        self.message_queue: List[str] = []

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.connected_clients.append({"websocket": websocket, "username": username})

    def disconnect(self, websocket: WebSocket):
        self.connected_clients = [
            client
            for client in self.connected_clients
            if client["websocket"] != websocket
        ]

    async def send_personal_message(self, websocket: WebSocket, username: str):
        welcome_message = f"Привет, {username}! Добро пожаловать в музыкальный плеер!"
        await websocket.send_text(welcome_message)

    async def send_welcome_message(self, websocket: WebSocket, username: str):
        for client in self.connected_clients:
            if client["websocket"] != websocket:
                await client["websocket"].send_text(
                    f"Пользователь, {username} присоединился в плеер!"
                )

    async def send_messages_from_queue(self, websocket: WebSocket):
        for message in self.message_queue:
            await websocket.send_text(message)

    def append_new_message(self, message: str):
        self.message_queue.append(message)

    async def broadcast(self, message: str):
        for client in self.connected_clients:
            await client["websocket"].send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    await manager.send_personal_message(websocket, username)
    await manager.send_messages_from_queue(websocket)
    await manager.send_welcome_message(websocket, username)

    try:
        while True:
            data = await websocket.receive_text()
            manager.append_new_message(data)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Пользователь {username} покинул плеер!")


@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
