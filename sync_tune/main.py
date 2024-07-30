from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI()

templates = Jinja2Templates(directory="templates")


class ConnectionManager:
	"""
	Управление подключениями и обменом сообщениями между клиентами.

	Атрибуты:
	connected_clients (list[WebSocket]): список подключенных клиентов (объектов WebSocket).
	message_queue (list[str]): очередь сообщений для отправки клиентам.
	"""

	def __init__(self):
		self.connected_clients: list[WebSocket, str] = []
		self.message_queue: list[str] = []

	async def connect(self, websocket: WebSocket, username: str):
		await websocket.accept()
		self.connected_clients.append({'websocket': websocket, 'username': username})

	def disconnect(self, websocket: WebSocket, username: str):
		self.connected_clients.remove({"websocket": websocket, "username": username})

	async def send_personal_message(self, websocket: WebSocket, username: str):
		welcome_message = f"Привет, {username}! Добро пожаловать в чат!"
		await websocket.send_text(welcome_message)

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

	try:
		while True:
			data = await websocket.receive_text()
			message = f"{username}: {data}"
			manager.append_new_message(message)
			await manager.broadcast(message)
	except WebSocketDisconnect:
		manager.disconnect(websocket, username)
		await manager.broadcast(f"Пользователь {username} покинул чат!")


@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
	return templates.TemplateResponse("chat.html", {"request": request})
