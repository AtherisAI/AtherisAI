import asyncio
import json
from typing import Dict, List
import websockets

connected_clients: List[websockets.WebSocketServerProtocol] = []

class RealTimeUpdateServer:
    def __init__(self, host: str = "localhost", port: int = 6789):
        self.host = host
        self.port = port
        self.queue = asyncio.Queue()
        print(f"[RealTimeUpdateServer] Initialized on ws://{host}:{port}")

    async def register(self, websocket):
        connected_clients.append(websocket)
        print(f"[RealTimeUpdateServer] Client connected: {websocket.remote_address}")

    async def unregister(self, websocket):
        connected_clients.remove(websocket)
        print(f"[RealTimeUpdateServer] Client disconnected: {websocket.remote_address}")

    async def send_updates(self):
        while True:
            data = await self.queue.get()
            if connected_clients:
                message = json.dumps(data)
                await asyncio.gather(*(client.send(message) for client in connected_clients))
                print(f"[RealTimeUpdateServer] Sent update to {len(connected_clients)} clients.")
            self.queue.task_done()

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            async for _ in websocket:
                pass
        finally:
            await self.unregister(websocket)

    def push_update(self, update: Dict):
        asyncio.create_task(self.queue.put(update))

    async def start(self):
        server = await websockets.serve(self.handler, self.host, self.port)
        await self.send_updates()
        await server.wait_closed()


# Example simulation
if __name__ == "__main__":
    server = RealTimeUpdateServer()

    async def simulate_updates():
        while True:
            update = {
                "type": "alert",
                "message": "Proposal XYZ just passed",
                "timestamp": asyncio.get_event_loop().time()
            }
            server.push_update(update)
            await asyncio.sleep(10)

    loop = asyncio.get_event_loop()
    loop.create_task(server.start())
    loop.create_task(simulate_updates())
    loop.run_forever()
