import json
import asyncio
from json.decoder import JSONDecodeError
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedError


class Server:
    """
    Websocket server handler
    """
    def __init__(self, debug=False):
        self.debug = debug
        self.clients = set()

    async def send(self, message: str):
        if len(self.clients):
            if self.debug:
                print(f"Send message '{message}' to registered clients")

            await asyncio.wait([client.send(message) for client in self.clients])

    async def handler(self, websocket: WebSocketServerProtocol, path: str):
        # Register new websocket client connection
        self.clients.add(websocket)

        try:
            if self.debug:
                print(f"Accept new client connection from {websocket.remote_address}")

            # Iteration terminates when the client disconnects like
            # https://websockets.readthedocs.io/en/stable/intro.html#consumer
            async for message in websocket:
                if self.debug:
                    print(f"Accept from {websocket.remote_address} message {message}")

        except ConnectionClosedError as e:
            if self.debug:
                print(e)
        finally:
            # Unregister websocket client connection on close it
            if self.debug:
                print(f"Remote connection closed {websocket.remote_address}")

            self.clients.remove(websocket)
            await websocket.close()
            await websocket.wait_closed()
