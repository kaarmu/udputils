
import socket

from collections.abc import Callable, Iterator
from typing import Optional

SockAddr = tuple[str, int]
MsgProc = Callable[[bytes], bytes]
MsgPred = Callable[[int, bytes], bool]

class Communicator:
    """UDP communicator.
    """

    socket: socket.socket
    local: SockAddr
    remotes: list[SockAddr]
    process_incoming: list[MsgProc]
    process_outgoing: list[MsgProc]

    @classmethod
    def Any(cls, *args, **kwargs) -> 'Communicator':
        """Connect to any socket."""
        return cls(('', 0), *args, **kwargs)

    def __init__(self, local: SockAddr, timeout: Optional[int] = None) -> None:
        self.remotes = []
        self.local = local or ('', 0)

        self.process_incoming = []
        self.process_outgoing = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.bind(self.local)

    def __del__(self) -> None:
        self.socket.close()

    def send(self, msg: bytes, *targets: int | slice | str, flags: int = 0) -> int:
        """Send a message to all targets."""

        # apply all pre-processing functions
        for proc in self.process_outgoing:
            msg = proc(msg)

        # send message to remotes
        for remote in self._fetchRemotes(*targets):
            self.socket.sendto(msg, flags, remote)

        return len(msg)

    def recv(self, bufsize: int, *, flags: int = 0) -> bytes:

        msg, addr = self.socket.recvfrom(bufsize, flags)

        # apply all post-processing functions
        for proc in self.process_incoming:
            msg = proc(msg)

        return msg, addr

    def _fetchRemotes(self, *targets: int | slice | tuple[str, int]) -> Iterator[str]:
        for target in targets:
            if isinstance(target, int):
                yield self.remotes[target]
            elif isinstance(target, slice):
                yield from self.remotes[target]
            elif isinstance(target, tuple):
                yield target
            else:
                raise TypeError("Invalid type of target.")

        if not targets:
            yield from self.remotes

            if not self.remotes:
                raise ValueError("You must specify at least one target.")



