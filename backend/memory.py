"""In-memory «память задачи» по session_id.

Backend держит по каждой сессии структурированное состояние диалога
(TaskState), обновляемое отдельным LLM-вызовом каждый ход (см. main.py).
Хранилище эфемерное: живёт в процессе, рестарт webchat.service его стирает —
это осознанный scope (durable SQLite «на потом»). Доступ сериализуется одним
asyncio.Lock: FastAPI однопроцессный, но два хода одной сессии могут пересечься.
"""

import asyncio
from collections import OrderedDict

from pydantic import BaseModel, Field

# Кап на число одновременно хранимых сессий. При переполнении выселяем самую
# давно использованную (LRU) — защита от неограниченного роста памяти на VPS.
MAX_SESSIONS = 500


class TaskState(BaseModel):
    """Структурированная память диалога. Пустые дефолты = «ещё ничего не знаем»."""

    goal: str = ""
    constraints: list[str] = Field(default_factory=list)
    terms: list[str] = Field(default_factory=list)
    clarified: list[str] = Field(default_factory=list)


class TaskMemory:
    """LRU-словарь {session_id → TaskState} под общим asyncio.Lock.

    Lock отдаётся наружу (`async with mem.lock:`), чтобы вызывающий мог атомарно
    выполнить read-modify-write: прочитать state, сходить в LLM за обновлением и
    записать результат, не переплетаясь с параллельным ходом той же сессии.
    """

    def __init__(self, max_sessions: int = MAX_SESSIONS):
        self._store: OrderedDict[str, TaskState] = OrderedDict()
        self._max = max_sessions
        self.lock = asyncio.Lock()

    def get(self, session_id: str) -> TaskState:
        """Вернуть state сессии (пустой, если ещё нет). Помечает как недавно
        использованную (move-to-end) для LRU."""
        state = self._store.get(session_id)
        if state is None:
            return TaskState()
        self._store.move_to_end(session_id)
        return state

    def set(self, session_id: str, state: TaskState) -> None:
        """Записать state, обновить LRU-порядок, выселить самую старую при переполнении."""
        self._store[session_id] = state
        self._store.move_to_end(session_id)
        while len(self._store) > self._max:
            self._store.popitem(last=False)
