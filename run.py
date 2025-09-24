import argparse
import asyncio
import logging
import sys

VERSION = "0.0.1"

from rpc_msg_pack_server.rpc_server import DebugRpcServer


class LogWriter:

    def __init__(self):
        self.file = None

    def __enter__(self):

        self.file = open('rpc_log.txt',mode='a', encoding='utf-8')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

    def debug_print(self, request: list):

        if request[0] == 0: # request
            req_id = request[1]
            method_name = request[2]
            params = request[3]
            print(f"Request id: {req_id}, method name: {method_name}, params: {params}")
        elif request[0] == 1:
            method_name = request[1]
            params = request[2]

            if method_name == 'LOGGER':
                for p in params:
                    self.file.write(f"{p}\n")
                    print(p)
            else:
                print(f'method_name = {method_name}, params = {params}')



async def run_rpc_server(host: str, port: int):

    with LogWriter() as log:
        server = DebugRpcServer(host, port, log.debug_print)
        try:
            await server.start()
            while True:
                await asyncio.sleep(3600)
        finally:
            server.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Debug RPC server')
    parser.add_argument('-b', '--bind', type=str, default='127.0.0.1')
    parser.add_argument('-p','--port',type=int, required=True)
    parser.add_argument('--version', action='version', version=f"{VERSION}")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run_rpc_server(args.bind, args.port))

    except KeyboardInterrupt:
        pass