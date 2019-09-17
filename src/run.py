#!/usr/bin/env python


import argparse
import asyncio
import websockets
from src import websocket, consumer

if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()

    # WEBSOCKET CONNECTION
    args_parser.add_argument('--wsaddr', default='127.0.0.1', help='IP address for websocket ws')
    args_parser.add_argument('--wspath', default='', help='Path to websocket')
    args_parser.add_argument('--wsport', default=8080, help='Port for websocket ws')

    # QUEUE MESSAGES SERVICE (RabbitMQ)
    args_parser.add_argument('--rmqhost', default='localhost', help='QUeue messages service host')
    args_parser.add_argument('--rmqport', default=5672, help='QUeue messages service port')
    args_parser.add_argument('--rmquser', default='guest', help='QUeue messages service user')
    args_parser.add_argument('--rmqpass', default='guest', help='QUeue messages service password')

    # DATABASE SOURCE (Postgresql)
    args_parser.add_argument('--dbshost', default='localhost', help='The geodetector database source of data host')
    args_parser.add_argument('--dbsport', default=5432, help='The geodetector database source of data port')
    args_parser.add_argument('--dbsuser', required=True, help='The geodetector database source of data user')
    args_parser.add_argument('--dbspass', required=True, help='The geodetector database source of data password')
    args_parser.add_argument('--dbsdb', required=True, help='The geodetector database source of data name/index')
    args_parser.add_argument('--debug', action='store_true', help='Debug mode turn on')

    args = args_parser.parse_args()

    loop = asyncio.get_event_loop()

    wssrv = websocket.Server(debug=args.debug)
    ws_task = websockets.serve(
        wssrv.handler,
        args.wsaddr,
        args.wsport
    )

    conssrv = consumer.Server(wssrv, loop, [], args)

    try:
        loop.run_until_complete(asyncio.wait([ws_task, conssrv.handler]))
    except KeyboardInterrupt:
        print("Keyboard interrupt signal accepted. Stopping")
    finally:
        loop.close()
