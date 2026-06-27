"""Cache Redis para o Projeto_54_HP.

Interface compatível com TTLCache (get/set) — substituição transparente.

Estratégia:
  - Conecta ao Redis via variáveis de ambiente PIFF_REDIS_HOST / PIFF_REDIS_PORT
  - Se Redis estiver indisponível, usa fallback em memória (dict)
  - Serialização JSON com suporte a datetime/Decimal/pandas/numpy via custom encoder
  - TTL configurável via PIFF_CACHE_TTL_SECONDS (default 300s)
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

try:
    import redis as _redis
    _HAS_REDIS = True
except ImportError:
    _redis = None  # type: ignore[assignment]
    _HAS_REDIS = False


class _CacheEncoder(json.JSONEncoder):
    """Encoder JSON que serializa pandas DataFrames, numpy, Decimal e datetime."""

    def default(self, obj: Any) -> Any:
        try:
            import pandas as pd
            if isinstance(obj, pd.DataFrame):
                return {"__pandas_df__": True, "columns": list(obj.columns), "data": obj.to_dict("records")}
            if isinstance(obj, pd.Series):
                return {"__pandas_series__": True, "data": obj.to_list()}
        except ImportError:
            pass
        try:
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        try:
            from decimal import Decimal
            if isinstance(obj, Decimal):
                return float(obj)
        except ImportError:
            pass
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        return super().default(obj)


def _cache_decoder(dct: dict) -> Any:
    """Decoder que reconstrói pandas DataFrames a partir do marcador __pandas_df__."""
    if "__pandas_df__" in dct:
        try:
            import pandas as pd
            return pd.DataFrame(dct["data"], columns=dct["columns"])
        except ImportError:
            return dct["data"]
    if "__pandas_series__" in dct:
        return dct["data"]
    return dct


class RedisCache:
    """Cache Redis com fallback em memória."""

    def __init__(self, ttl_seconds: int | None = None):
        self.ttl = ttl_seconds or int(os.getenv("PIFF_CACHE_TTL_SECONDS", "300"))
        self._connected = False
        self._client: _redis.Redis | None = None  # type: ignore[assignment]
        self._fallback: dict[str, tuple[float, Any]] = {}

        if _HAS_REDIS:
            try:
                host = os.getenv("PIFF_REDIS_HOST", "localhost")
                port = int(os.getenv("PIFF_REDIS_PORT", "6379"))
                self._client = _redis.Redis(
                    host=host,
                    port=port,
                    socket_connect_timeout=2,
                    decode_responses=True,
                )
                self._client.ping()
                self._connected = True
            except Exception:
                self._connected = False

    @property
    def available(self) -> bool:
        return self._connected

    # ---- interface pública (compatível com TTLCache) ----

    def get(self, key: str) -> Any | None:
        if self._connected and self._client:
            try:
                raw = self._client.get(key)
                if raw is not None:
                    return json.loads(raw, object_hook=_cache_decoder)
                return None
            except Exception:
                return self._fallback_get(key)
        return self._fallback_get(key)

    def set(self, key: str, value: Any) -> None:
        if self._connected and self._client:
            try:
                serialized = json.dumps(value, cls=_CacheEncoder, ensure_ascii=False)
                self._client.setex(key, self.ttl, serialized)
                return
            except Exception:
                pass
        self._fallback_set(key, value)

    def delete(self, key: str) -> None:
        if self._connected and self._client:
            try:
                self._client.delete(key)
            except Exception:
                pass
        self._fallback.pop(key, None)

    def flush(self) -> None:
        if self._connected and self._client:
            try:
                self._client.flushdb()
            except Exception:
                pass
        self._fallback.clear()

    # ---- fallback em memória (TTLCache-like) ----

    def _fallback_get(self, key: str) -> Any | None:
        entry = self._fallback.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at < time.time():
            self._fallback.pop(key, None)
            return None
        return value

    def _fallback_set(self, key: str, value: Any) -> None:
        self._fallback[key] = (time.time() + self.ttl, value)

    def __repr__(self) -> str:
        status = "Redis" if self._connected else "Memória (fallback)"
        return f"<RedisCache:{status} ttl={self.ttl}s>"
