import logging
from typing import List
from models import Client


class ConnectionManager:
    """
    Управление подключениями и обменом сообщениями между клиентами.

    Атрибуты:
    connected_clients (List[Client]): Список подключенных клиентов.
    message_queue (List[str]): Очередь сообщений для отправки клиентам.
    """

    def __init__(self):
        self.connected_clients: List[Client] = []
        self.message_queue: List[str] = []

    async def connect(self, client: Client):
        """Принятие нового соединения"""
        await client.websocket.accept()
        self.connected_clients.append(client)
        logging.info("Клиент %s успешно подключен", client.username)

    async def disconnect(self, client: Client):
        """Отключение клиента"""
        self.connected_clients = [
            existing_client
            for existing_client in self.connected_clients
            if existing_client.websocket != client.websocket
        ]
        logging.info("Клиент %s отключился", client.username)

    async def send_welcome_message(self, client: Client):
        """Отправка приветственного сообщения пользователю"""
        welcome_message = (
            f"Привет, {client.username}! Добро пожаловать в музыкальный плеер!"
        )
        await client.websocket.send_text(welcome_message)

    async def notify_others_about_new_client(self, client: Client):
        """Уведомление других клиентов о новом пользователе"""
        for existing_client in self.connected_clients:
            if existing_client.websocket != client.websocket:
                await existing_client.websocket.send_text(
                    f"Пользователь {client.username} присоединился в плеер!"
                )

    async def send_messages_from_queue(self, client: Client):
        """Отправка накопленных сообщений новому клиенту"""
        for message in self.message_queue:
            await client.websocket.send_text(message)

    def append_new_message(self, message: str):
        """Добавление нового сообщения в очередь"""
        self.message_queue.append(message)
        logging.info("Новое сообщение добавлено в очередь: %s", message)

    async def broadcast(self, message: str):
        """Рассылка сообщения всем клиентам"""
        for client in self.connected_clients:
            await client.websocket.send_text(message)
        logging.info("Широковещательное сообщение: %s", message)

    async def initialize_client_session(self, client: Client):
        """Инициализация сессии клиента"""
        await self.send_messages_from_queue(client)
        await self.send_welcome_message(client)
        await self.notify_others_about_new_client(client)
