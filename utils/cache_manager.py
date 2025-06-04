import time
from typing import Any, Dict, Optional

class CacheEntry:
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.timestamp = time.time()
        self.ttl = ttl

    def is_valid(self) -> bool:
        if self.ttl is None:
            return True
        return time.time() < self.timestamp + self.ttl


class CacheManager:
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        print("[CacheManager] Initialized.")

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        self.cache[key] = CacheEntry(value, ttl)
        print(f"[CacheManager] Set key: {key} with TTL: {ttl}")

    def get(self, key: str) -> Optional[Any]:
        entry = self.cache.get(key)
        if entry and entry.is_valid():
            print(f"[CacheManager] Hit for key: {key}")
            return entry.value
        elif entry:
            print(f"[CacheManager] Expired key: {key}")
            del self.cache[key]
        else:
            print(f"[CacheManager] Miss for key: {key}")
        return None

    def clear(self):
        self.cache.clear()
        print("[CacheManager] Cache cleared.")

    def cleanup(self):
        expired_keys = [k for k, v in self.cache.items() if not v.is_valid()]
        for k in expired_keys:
            del self.cache[k]
            print(f"[CacheManager] Removed expired key: {k}")


# Example usage
if __name__ == "__main__":
    cache = CacheManager()
    cache.set("solana_data", {"price": 19.8}, ttl=5)

    time.sleep(2)
    print(cache.get("solana_data"))

    time.sleep(4)
    print(cache.get("solana_data"))

    cache.set("user_status", "active")
    print(cache.get("user_status"))

    cache.cleanup()
