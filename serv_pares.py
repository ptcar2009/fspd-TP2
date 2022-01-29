#!/bin/env python3
from concurrent import futures
import logging
import socket
import threading
from cli_central import CentralImpl
from util import usage
import sys

import grpc
import pares_pb2
import pares_pb2_grpc


class DoStuff(pares_pb2_grpc.ParesServicer):
    def __init__(self, id: str, stop_event: threading.Event, has_activate) -> None:
        self.store = {}
        self.id = id
        self._stop_event = stop_event
        self.has_activate = has_activate
        super().__init__()

    def Insert(self, request, _):
        logging.debug("received insert request. key: %s, value %s" %
                      (request.key, request.value))

        if request.key in self.store:
            logging.debug("key already exists. key: %s, value %s" %
                          (request.key, request.value))
            return pares_pb2.InsertReply(result=-1)

        logging.debug("inserting key. key: %s, value %s" %
                      (request.key, request.value))
        self.store[request.key] = request.value
        return pares_pb2.InsertReply(result=0)

    def Consult(self, request, _):
        logging.debug("received consult request. key: %s" % request.key)

        if request.key not in self.store:
            logging.debug("key does not exist. key: %s" % request.key)
            return pares_pb2.ConsultReply(value="")

        logging.debug("recovering key. key: %s" % request.key)
        return pares_pb2.ConsultReply(value=self.store[request.key])

    def Activate(self, request, _):
        logging.debug("received activate request. id: %s" % request.id)

        # if does not have activate, simply skip and return zero
        if self.has_activate:
            cli_central = CentralImpl(request.id)
            ret = cli_central.Register(self.id, list(self.store.keys()))
            cli_central.Close()
            return pares_pb2.ActivateReply(ret=ret)

        return pares_pb2.ActivateReply(ret=0)

    def Terminate(self, _, __):
        logging.debug("received terminate request.")

        # on terminate, set the thread event so the main thread can exit
        self._stop_event.set()
        return pares_pb2.ActivateReply(ret=0)


def serve():
    # event for shutting down server on terminate
    stop_event = threading.Event()

    if len(sys.argv) < 2:
        usage()
        exit(1)

    # if there's a second argument, activate the activate method
    has_activate = False
    if len(sys.argv) > 2:
        has_activate = True

    id = socket.getfqdn()
    logging.info("activating server on port %s", sys.argv[1])
    logging.debug("setting hostname to %s" % id)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    pares_pb2_grpc.add_ParesServicer_to_server(
        DoStuff(f'{id}:{sys.argv[1]}', stop_event, has_activate), server)
    server.add_insecure_port(f'0.0.0.0:{sys.argv[1]}')

    # starting the server and wating for terminate request
    server.start()
    stop_event.wait()
    server.stop(None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    serve()
