#!/bin/env python3
from typing import List
import central_pb2
import central_pb2_grpc
from util import cli_command
from cli_pares import ParesImpl
import sys
import grpc


class CentralImpl():
    def __init__(self, address):
        self.channel = grpc.insecure_channel(address)
        self.stub = central_pb2_grpc.CentralStub(self.channel)

    def Register(self, id: str, keys: List[int]) -> int:
        return self.stub.Register(central_pb2.RegisterRequest(id=id, keys=keys)).result

    def Map(self, key: int) -> str:
        return self.stub.Map(central_pb2.MapRequest(key=key)).id

    def Terminate(self) -> int:
        return self.stub.Terminate(central_pb2.TerminateRequest()).ret

    def Close(self):
        self.channel.close()


def usage():
    print(f"usage: {sys.argv[0]} <server_identifier>")

def commands():
    # print("Available commands:")
    # print("I,key, description - add a key")
    # print("C,key - consult a key")
    # print("A, identifier - activate service as identifier")
    # print("T - terminate")
    pass

cli_commands = {}


@cli_command("C", cli_commands)
def consult_command(command, client):
    if len(command) != 2:
        print("invalid command syntax")
        commands()
        return False
    try:
        key = int(command[1])
    except:
        print('invalid key')
        return False
    id = client.Map(key)
    par_cli = ParesImpl(id)
    print(f'{id}:', par_cli.Consult(key))
    par_cli.Close()


@cli_command("T", cli_commands)
def terminate_command(_, client):
    print(client.Terminate())
    client.Close()
    return True

def help_command(command, client):
    commands()
    return False

def run():
    if len(sys.argv) < 2:
        usage()
        exit(1)
    client = CentralImpl(sys.argv[1])
    while(True):
        command = input().split(',')
        if cli_commands.get(command[0], help_command)(command, client):
            break


if __name__ == "__main__":
    run()
