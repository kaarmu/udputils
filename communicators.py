
from socket import socket, AF_INET, SOCK_DGRAM
from collections.abc import Callable
from typing import Optional
import itertools

SockAddr = tuple[str, int]
MsgProc = Callable[[bytes], bytes]
MsgPred = Callable[[int, bytes], bool]

class Communicator:

    socket: socket
    local: SockAddr
    remotes: list[SockAddr]
    process_incoming: list[MsgProc]
    process_outgoing: list[MsgProc]

    def __init__(self, local: SockAddr = None, timeout: Optional[int] = None):
        self.remotes = []
        self.local = local or ('', 0)

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.bind(self.local)

    def __del__(self):
        self.socket.close()

    def send(self, msg: bytes, *targets: int, flags: int = 0) -> int:
        targets = targets or range(len(self.remotes))

        for proc in self.process_outgoing:
            msg = proc(msg)

        for remote in map(lambda i: self.remotes[i], targets):
            self.socket.sendto(msg, flags, remote)

        return len(msg)

    def recv(self, bufsize: int, flags: int = 0) -> bytes:
        msg, addr = self.socket.recvfrom(bufsize, flags)

        for proc in self.process_incoming:
            msg = proc(msg)

        return msg, addr








