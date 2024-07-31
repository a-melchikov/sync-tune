from dataclasses import dataclass
from fastapi import WebSocket


@dataclass
class Client:
    """
    Класс для представления клиента.

    Атрибуты:
    websocket (WebSocket): WebSocket соединение.
    username (str): Имя пользователя.
    """

    websocket: WebSocket
    username: str
