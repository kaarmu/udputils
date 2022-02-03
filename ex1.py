from communicators import Communicator

if __name__ == '__main__':
    c = Communicator(('', 3000))
    msg = b''

    while msg != b'quit':
        msg, addr = c.recv(10)
        print(f'received "{msg}" from {addr}')
        rep = msg
        if msg == b'add':
            c.remotes.append(addr)
            rep = f'address {addr} added!'.encode()
        if msg == b'rem' and addr in c.remotes:
            c.remotes.remove(addr)
            rep = f'address {addr} removed!'.encode()
        c.send(rep, addr)
