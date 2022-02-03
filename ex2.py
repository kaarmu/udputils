from communicators import Communicator

if __name__ == '__main__':
    c = Communicator.Any()
    req = lambda msg: c.send(msg, ('', 3000)) and c.recv(10)[0]
