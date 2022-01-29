import sys
def cli_command(key, d):
    def add_to_key(f):
        d[key] = f
        return f
    return add_to_key

def usage():
    print(f"usage: {sys.argv[0]} <server_identifier>")
