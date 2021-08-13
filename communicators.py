
from socket import socket, AF_INET, SOCK_DGRAM
from collections.abc import Callable
from typing import Optional, Union
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

    @classmethod
    def Any(cls, *args, **kwargs):
        return cls(('', 0), *args, **kwargs)

    def __init__(self, local: SockAddr, timeout: Optional[int] = None):
        self.remotes = []
        self.local = local or ('', 0)

        self.process_incoming = []
        self.process_outgoing = []

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.bind(self.local)

    def __del__(self):
        self.socket.close()

    def send(self, msg: bytes, *targets: Union[int, slice], flags: int = 0) -> int:

        for proc in self.process_outgoing:
            msg = proc(msg)

        remotes = reduce(
            lambda p, q: p + q,
            map(lambda i: self.remotes[i],
                filter(lambda t: isinstance(t, int), targets)),
            itertools.chain.from_iterable(map(
                lambda slc: yield from self.remotes[i],
                filter(lambda t: isinstance(t, slice), targets)
            )),
            list()
        )

        for remote in remotes:
            self.socket.sendto(msg, flags, remote)

        return len(msg)

    def recv(self, bufsize: int, *, flags: int = 0) -> bytes:
        msg, addr = self.socket.recvfrom(bufsize, flags)

        for proc in self.process_incoming:
            msg = proc(msg)

        return msg, addr








