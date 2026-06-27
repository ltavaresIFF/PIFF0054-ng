"""Performance benchmark: mede load_test completo com os 3 layers de cache.

RODAR COM:   python bench.py
"""
import time, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
from src.config.settings import SETTINGS
from src.infrastructure.sql.connection import SqlServerConnection
from src.infrastructure.sql.repositories import SqlTestQueryRepository
from src.infrastructure.cache import TTLCache
from src.application.services import TestReadService

OUTPUT: list[str] = []


def log(msg: str) -> None:
    OUTPUT.append(msg)


conn = SqlServerConnection(SETTINGS)
cache = TTLCache(ttl_seconds=300)
repo = SqlTestQueryRepository(conn)
svc = TestReadService(repo, cache)

# --- COLD: 1a chamada (todos os caches vazios) ---
t0 = time.perf_counter()
r = svc.load_test(1, "C01_TESTE_001")
t_cold = (time.perf_counter() - t0) * 1000
log(f"load_test COLD (sem cache) : {t_cold:6.0f} ms  rows={len(r.rows)}")

# --- HOT: 2a chamada (TTLCache + column cache) ---
t0 = time.perf_counter()
r2 = svc.load_test(1, "C01_TESTE_001")
t_hot = (time.perf_counter() - t0) * 1000
log(f"load_test HOT  (TTL cache): {t_hot:6.0f} ms  rows={len(r2.rows)}")

# --- list_test_ids COLD ---
t0 = time.perf_counter()
ids = svc.list_test_ids(1)
log(f"list_test_ids COLD        : {(time.perf_counter()-t0)*1000:6.0f} ms  ids={len(ids)}")

# --- list_test_ids HOT ---
t0 = time.perf_counter()
ids = svc.list_test_ids(1)
log(f"list_test_ids HOT         : {(time.perf_counter()-t0)*1000:6.0f} ms  ids={len(ids)}")

# --- 1000 rows simulation (cyl 3 or 6 for varied data) ---
t0 = time.perf_counter()
r3 = svc.load_test(6, "C06_TESTE_001")
t_1k = (time.perf_counter() - t0) * 1000
log(f"load_test COLD cyl6       : {t_1k:6.0f} ms  rows={len(r3.rows)}")

conn.close()

with open("perf_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(OUTPUT) + "\n")
print("Wrote perf_result.txt", flush=True)
