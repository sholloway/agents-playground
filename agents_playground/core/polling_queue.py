from __future__ import annotations

from collections import deque
import socket
from typing import Any, Callable


class PollingQueue(deque):
    def __init__(self, item_processor: Callable) -> None:
        super().__init__()
        self._put_socket, self._get_socket = socket.socketpair()
        self._item_processor: Callable = item_processor

    def fileno(self):
        return self._get_socket.fileno()

    def append(self, item: Any) -> None:
        super().append(item)
        self._put_socket.send(b"x")

    def popleft(self) -> Any:
        self._get_socket.recv(1)
        return super().popleft()

    def process_item(self) -> None:
        item = self.popleft()
        self._item_processor(item)
