import argparse
import asyncio
import logging


VERSION = "0.0.1"

from rpc_msg_pack_server.rpc_server import run_rpc_server

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