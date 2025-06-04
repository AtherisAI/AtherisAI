import time
from threading import Timer as ThreadingTimer
from typing import Callable, Dict

class RepeatingTimer:
    def __init__(self, interval: float, function: Callable, name: str = "UnnamedTimer"):
        self.interval = interval
        self.function = function
        self.name = name
        self.thread_timer: ThreadingTimer = None
        self.is_running = False
        self.start_time = None

    def _run(self):
        self.is_running = False
        self.start()
        print(f"[{self.name}] Executing function at {time.time()}")
        self.function()

    def start(self):
        if not self.is_running:
            self.thread_timer = ThreadingTimer(self.interval, self._run)
            self.thread_timer.start()
            self.is_running = True
            self.start_time = time.time()
            print(f"[{self.name}] Started with interval {self.interval}s")

    def stop(self):
        if self.thread_timer:
            self.thread_timer.cancel()
        self.is_running = False
        print(f"[{self.name}] Stopped")

    def reset(self, new_interval: float = None):
        self.stop()
        if new_interval:
            self.interval = new_interval
            print(f"[{self.name}] Interval reset to {self.interval}s")
        self.start()


class GlobalTimerRegistry:
    def __init__(self):
        self.timers: Dict[str, RepeatingTimer] = {}
        print("[GlobalTimerRegistry] Initialized")

    def register(self, name: str, interval: float, function: Callable):
        if name in self.timers:
            raise Exception(f"Timer with name '{name}' already exists.")
        timer = RepeatingTimer(interval, function, name)
        self.timers[name] = timer
        timer.start()
        print(f"[GlobalTimerRegistry] Registered and started timer '{name}'")

    def stop_timer(self, name: str):
        if name in self.timers:
            self.timers[name].stop()
            del self.timers[name]
            print(f"[GlobalTimerRegistry] Stopped and removed timer '{name}'")

    def stop_all(self):
        for name, timer in list(self.timers.items()):
            timer.stop()
        self.timers.clear()
        print("[GlobalTimerRegistry] All timers stopped")


# Example usage
if __name__ == "__main__":
    def ping():
        print("Ping from Atheris global timer")

    registry = GlobalTimerRegistry()
    registry.register("ping_timer", 3, ping)

    time.sleep(10)
    registry.stop_all()
