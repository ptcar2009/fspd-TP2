#!/bin/env python
import sys
import grpc
import pares_pb2_grpc
import pares_pb2

from util import cli_command


class ParesImpl():
    def __init__(self, address):
        self.channel = grpc.insecure_channel(address)
        self.stub = pares_pb2_grpc.ParesStub(self.channel)

    def Insert(self, key: int, value: str) -> int:
        return self.stub.Insert(pares_pb2.InsertRequest(key=key, value=value)).result

    def Consult(self, key: int) -> str:
        return self.stub.Consult(pares_pb2.ConsultRequest(key=key)).value

    def Activate(self, id: str) -> int:
        return self.stub.Activate(pares_pb2.ActivateRequest(id=id)).ret

    def Terminate(self) -> int:
        return self.stub.Terminate(pares_pb2.TerminateRequest()).ret

    def Close(self):
        self.channel.close()


def usage():
    print(f"usage: {sys.argv[0]} <server_identifier>")


def commands():
    print("Available commands:")
    print("I,key, description - add a key")
    print("C,key - consult a key")
    print("A, identifier - activate service as identifier")
    print("T - terminate")
    pass


command_dict = {}


@cli_command("I", command_dict)
def insert_command(command, client):
    if len(command) != 3:
        print("invalid command syntax")
        commands()
        return False

    try:
        key = int(command[1])
    except:
        print('invalid key')
        return False
    value = command[2]
    result = client.Insert(key, value)
    print(result)
    return False


@cli_command("C", command_dict)
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

    print(client.Consult(key))
    return False


@cli_command("A", command_dict)
def activate_command(command, client):
    if len(command) != 2:
        print("invalid command syntax")
        commands()
        return False
    id = command[1]
    print(client.Activate(id))
    return False


@cli_command("T", command_dict)
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
    client = ParesImpl(sys.argv[1])
    while(True):
        command = input('> ').split(',')
        if command_dict.get(command[0], help_command)(command, client):
            break


if __name__ == "__main__":
    run()
