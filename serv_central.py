#!/bin/env python3
from concurrent import futures
import logging
import sys
import threading

import grpc
import central_pb2
import central_pb2_grpc
from util import usage


class DoStuff(central_pb2_grpc.CentralServicer):
    def __init__(self, stop_event: threading.Event) -> None:
        self.store = {}
        self._stop_event = stop_event
        super().__init__()

    def Register(self, request, _):
        for key in request.keys:
            self.store[key] = request.id
        return central_pb2.RegisterReply(result=len(request.keys))

    def Map(self, request, _):
        logging.debug("received consult request. key: %s" % request.key)

        if request.key not in self.store:
            logging.debug("key does not exist. key: %s" % request.key)
            return central_pb2.MapReply(id="")

        logging.debug("recovering key. key: %s" % request.key)
        return central_pb2.MapReply(id=self.store[request.key])

    def Terminate(self, _, __):
        logging.debug("received terminate request.")

        # setting stop event to stop main thread
        self._stop_event.set()
        return central_pb2.TerminateReply(ret=0)


def serve():
    if len(sys.argv) < 2:
        usage()
        exit(1)

    # thread event for terminate request
    stop_event = threading.Event()

    logging.info("activating server on port %s", sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    central_pb2_grpc.add_CentralServicer_to_server(DoStuff(stop_event), server)
    server.add_insecure_port(f'0.0.0.0:{sys.argv[1]}')

    # starting server and waiting for termination request
    server.start()
    stop_event.wait()
    server.stop(None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    serve()
