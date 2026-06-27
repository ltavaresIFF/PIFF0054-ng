"""@brief Cache simples em memória com expiração por TTL.

Implementa a interface TTLCache (get/set) usando um dicionário em memória
com expiração automática de entradas. Usado como fallback quando o Redis
não está disponível.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _Entry:
    """@brief Entrada interna do cache com valor e timestamp de expiração.

    @param value Dado armazenado.
    @param expires_at Timestamp Unix de quando a entrada expira.
    """
    value: Any
    expires_at: float


class TTLCache:
    """@brief Cache LRU simplificado com expiração por tempo (TTL).

    Thread-safe para uso single-thread (Streamlit). As entradas expiradas
    são removidas na próxima tentativa de leitura (lazy eviction).
    """

    def __init__(self, ttl_seconds: int):
        """@brief Inicializa o cache com TTL fixo.

        @param ttl_seconds Tempo de vida padrão das entradas em segundos.
        """
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, _Entry] = {}

    def get(self, key: str) -> Any | None:
        """@brief Recupera um valor do cache, ou None se ausente/expirado.

        @param key Chave da entrada.
        @return Valor armazenado ou None.
        """
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at < time.time():
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: Any) -> None:
        """@brief Armazena um valor no cache com o TTL configurado.

        @param key Chave da entrada.
        @param value Valor a armazenar.
        """
        self._store[key] = _Entry(value=value, expires_at=time.time() + self.ttl_seconds)
