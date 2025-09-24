import asyncio
import logging

import msgpack
from typing import Any, Callable, List







logger = logging.getLogger('rpc_msg_pack_server')

REQUEST = 0
RESPONSE = 1
NOTIFY = 2

# Request [0, request_id, "method_name", [param1, param2, ...]]
# Response [1, request_id, error, result]
# Notify [2, "event_name", [param1, param2, ...]]

class DebugRpcServer:
    def __init__(self, host: str, port, callback:callable) -> None:

        self._host = host
        self._port = port
        self._callback = callback

        self._running_tasks = {}

    async def start(self) -> None:
        task = asyncio.create_task(self._start())
        self._running_tasks['SERVER'] = task
        task.add_done_callback(lambda x: self._running_tasks.pop('SERVER', None))

    async def _start(self):
        server = None
        while True:
            try:
                server = await asyncio.start_server(self.handle_client, self._host, self._port)
                addr = server.sockets[0].getsockname()
                logger.info(f"RPC Server listening on {addr}")
                async with server:
                    await server.serve_forever()
            except asyncio.CancelledError:
                logger.info(f"Server stopped {self._host}:{self._port}")
                return
            except Exception as e:
                logger.exception(f'RPC Server error: {e}, reconnect')
                await asyncio.sleep(1)
                if server:
                    server.close()

    def stop(self):
        task = self._running_tasks.get('SERVER', None)
        if task:
            task.cancel()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        unpacker = msgpack.Unpacker(raw=False)

        while True:
            try:
                chunk = await reader.read(1024)
                logger.debug(f'{chunk}')
                if not chunk:
                    break

                unpacker.feed(chunk)

                for request in unpacker:
                    logger.debug(f'{request}')
                    self._callback(request)
            except (asyncio.IncompleteReadError, ConnectionResetError):
                break
            except Exception as e:
                logger.exception(f"Error on server: {e}")
                break

        writer.close()
        await writer.wait_closed()

    async def _handle_notify(self, request: List):
        method_name = request[1]
        params = request[2]
        logger.info(f"Notify: {method_name} {params}")

    async def _handle_request(self, request: List, writer: asyncio.StreamWriter):

        req_id = request[1]
        method_name = request[2]
        params = request[3]
        logger.info(f"Request: name = {method_name}, req_id={req_id}, params = {params}")

    async def _send_error(self, writer: asyncio.StreamWriter, req_id: Any, error_msg: str):
        response = {
            "id": req_id,
            "result": None,
            "error": error_msg
        }
        await self._send_message_response(writer, response)

    @staticmethod
    async def _send_message_response(writer: asyncio.StreamWriter, msg: dict):

        raw_msg = [RESPONSE, msg["id"], msg["error"], msg["result"]]

        packed = msgpack.packb(raw_msg, use_bin_type=True)
        writer.write(packed)
        await writer.drain()
